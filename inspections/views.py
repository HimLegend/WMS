from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from weasyprint import HTML
from .forms import InspectionReportForm, FindingFormSet, PartFormSet, ConsumableFormSet
from .models import InspectionReport, InspectionFinding
from jobcards.models import JobCard


@login_required
def create_inspection_report(request, jobcard_id):
    job_card = get_object_or_404(JobCard, id=jobcard_id)

    # Redirect if already exists
    if hasattr(job_card, 'inspection_report'):
        return redirect('inspections:inspection_detail', pk=job_card.inspection_report.id)

    if request.method == 'POST':
        report_form = InspectionReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.job_card = job_card
            report.created_by = request.user
            report.save()
            messages.success(request, 'Inspection report created successfully.')
            return redirect('inspections:inspection_detail', pk=report.id)
        else:
            messages.error(request, 'Please fix errors in the form.')
    else:
        report_form = InspectionReportForm()

    return render(request, 'inspections/create.html', {
        'jobcard': job_card,
        'report_form': report_form,
    })


@login_required
def edit_inspection_report(request, pk):
    report = get_object_or_404(InspectionReport, pk=pk)

    # Formsets
    finding_formset = FindingFormSet(request.POST or None, instance=report)

    part_formsets = []
    consumable_formsets = []

    if request.method == 'POST':
        # Create Part/Consumable formsets for each finding with POST data
        valid = finding_formset.is_valid()

        for i, finding_form in enumerate(finding_formset.forms):
            finding_instance = finding_form.instance if finding_form.instance.pk else None
            part_fs = PartFormSet(
                request.POST, prefix=f'parts-{i}', instance=finding_instance
            )
            consumable_fs = ConsumableFormSet(
                request.POST, prefix=f'consumables-{i}', instance=finding_instance
            )
            part_formsets.append(part_fs)
            consumable_formsets.append(consumable_fs)

            if not part_fs.is_valid() or not consumable_fs.is_valid():
                valid = False

        if valid:
            report.updated_at = timezone.now()
            report.save()

            findings = finding_formset.save(commit=False)
            # Save findings and nested formsets
            for i, finding in enumerate(findings):
                finding.inspection = report
                finding.save()

                part_formsets[i].instance = finding
                consumable_formsets[i].instance = finding

                part_formsets[i].save()
                consumable_formsets[i].save()

            # Delete findings marked for deletion
            for finding in finding_formset.deleted_objects:
                finding.delete()

            messages.success(request, "Inspection report updated successfully.")
            return redirect('inspections:inspection_detail', pk=report.id)
        else:
            messages.error(request, "Please fix errors in the form and nested parts/consumables.")
    else:
        # GET: prepare nested formsets for existing findings
        for i, finding_form in enumerate(finding_formset.forms):
            finding_instance = finding_form.instance if finding_form.instance.pk else None
            part_formsets.append(PartFormSet(prefix=f'parts-{i}', instance=finding_instance))
            consumable_formsets.append(ConsumableFormSet(prefix=f'consumables-{i}', instance=finding_instance))

    return render(request, 'inspections/edit_nested.html', {
        'report_form': InspectionReportForm(instance=report),
        'finding_formset': finding_formset,
        'part_formsets': part_formsets,
        'consumable_formsets': consumable_formsets,
        'report': report,
    })


@login_required
def inspection_list(request):
    reports = InspectionReport.objects.select_related('job_card__vehicle').order_by('-created_at')
    return render(request, 'inspections/list.html', {'reports': reports})


@login_required
def inspection_detail(request, pk):
    job_card = get_object_or_404(JobCard, id=pk)
    report = get_object_or_404(InspectionReport, job_card=job_card)
    findings = report.findings.prefetch_related('parts', 'consumables')
    return render(request, 'inspections/detail.html', {
        'report': report,
        'findings': findings,
        'jobcard': job_card,
    })


@login_required
def inspection_pdf(request, pk):
    inspection = get_object_or_404(InspectionReport, job_card=pk)
    findings = inspection.findings.prefetch_related('parts', 'consumables')

    html_string = render_to_string('inspections/pdf.html', {
        'inspection': inspection,
        'findings': findings,
    })

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inspection_report_{inspection.id}.pdf"'
    return response
