# quotations/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemFormSet
from jobcards.models import JobCard
from django.views import View
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


class QuotationListView(ListView):
    model = Quotation
    template_name = 'quotations/list.html'
    context_object_name = 'quotations'
    ordering = ['-created_at']

class QuotationDetailView(DetailView):
    model = Quotation
    template_name = 'quotations/detail.html'
    context_object_name = 'quotation'

class QuotationCreateView(CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.jobcard = get_object_or_404(JobCard, pk=self.kwargs['jobcard_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobcard'] = self.jobcard
        if self.request.POST:
            context['formset'] = QuotationItemFormSet(self.request.POST)
        else:
            context['formset'] = QuotationItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        form.instance.jobcard = self.jobcard
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect('quotation_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class QuotationUpdateView(UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = QuotationItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = QuotationItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect('quotation_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

# Create PDF Quotations

class QuotationPDFView(View):
    # Register fonts
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    pdfmetrics.registerFont(TTFont('Oswald-Bold', os.path.join(font_dir, 'Oswald-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Oswald', os.path.join(font_dir, 'Oswald-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Poppins-Bold', os.path.join(font_dir, 'Poppins-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Poppins', os.path.join(font_dir, 'Poppins-Regular.ttf')))
    def get(self, request, pk, *args, **kwargs):
        quotation = Quotation.objects.get(pk=pk)
        jobcard = quotation.jobcard
        customer = jobcard.customer
        vehicle = jobcard.vehicle

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Quotation-{quotation.quotation_number}.pdf'

        buffer = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # Margins
        x_margin = 30
        y = height - 30

        # Logo
        logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
        if os.path.exists(logo_path):
            buffer.drawImage(logo_path, x_margin, y - 50, width=100, height=40, mask='auto')

        # Header
        buffer.setFont("Oswald-Bold", 14)
        buffer.drawString(x_margin + 120, y, "Ultra Premium Auto Care Services LLC")

        buffer.setFont("Oswald", 9)
        buffer.drawString(x_margin + 120, y - 15, "Dubai, UAE")
        buffer.drawString(x_margin + 120, y - 30, "Phone: +97148818838 | info@ultrapremium.vip")
        buffer.drawString(x_margin + 120, y - 45, "TRN: 100541878800003")

        y -= 80
        buffer.setFont("Oswald-Bold", 12)
        buffer.drawString(x_margin, y, f"QUOTATION #: {quotation.quotation_number}")
        buffer.drawString(width - 150, y, f"Date: {quotation.date_created.strftime('%Y-%m-%d')}")

        # Bill To
        y -= 30
        buffer.setFont("Poppins-Bold", 10)
        buffer.drawString(x_margin, y, "BILL TO")
        buffer.setFont("Poppins", 9)
        buffer.drawString(x_margin, y - 15, f"Name: {customer.name}")
        buffer.drawString(x_margin, y - 30, f"Phone: {customer.phone}")
        buffer.drawString(x_margin, y - 45, f"Company: {customer.company or '-'}")
        buffer.drawString(x_margin, y - 60, f"TRN: {customer.trn or '-'}")

        # Vehicle Info
        buffer.setFont("Poppins-Bold", 10)
        buffer.drawString(width / 2, y, "VEHICLE INFO")
        buffer.setFont("Poppins", 9)
        buffer.drawString(width / 2, y - 15, f"Make: {vehicle.make}")
        buffer.drawString(width / 2, y - 30, f"Model: {vehicle.model}")
        buffer.drawString(width / 2, y - 45, f"Year: {vehicle.year}")
        buffer.drawString(width / 2, y - 60, f"Plate: {vehicle.plate}")
        buffer.drawString(width / 2, y - 75, f"VIN: {vehicle.vin}")
        buffer.drawString(width / 2, y - 90, f"Mileage: {vehicle.mileage} km")

        y -= 110

        # Table Headers
        buffer.setFont("Poppins-Bold", 10)
        buffer.drawString(x_margin, y, "Qty")
        buffer.drawString(x_margin + 50, y, "Description")
        buffer.drawString(width - 150, y, "Unit Price")
        buffer.drawString(width - 80, y, "Amount")

        y -= 15
        buffer.setFont("Poppins", 9)

        # Table Rows
        for item in quotation.items.all():
            if y < 100:
                buffer.showPage()
                y = height - 100
            buffer.drawString(x_margin, y, str(item.quantity))
            buffer.drawString(x_margin + 50, y, item.description)
            buffer.drawRightString(width - 90, y, f"AED {item.unit_price:.2f}")
            buffer.drawRightString(width - 20, y, f"AED {item.line_total():.2f}")
            y -= 15

        # Totals
        y -= 15
        buffer.setFont("Poppins-Bold", 10)
        buffer.drawRightString(width - 90, y, "Subtotal:")
        buffer.drawRightString(width - 20, y, f"AED {quotation.subtotal:.2f}")

        y -= 15
        buffer.drawRightString(width - 90, y, f"Discount ({quotation.discount_percentage}%):")
        buffer.drawRightString(width - 20, y, f"-AED {quotation.discount_amount:.2f}")

        y -= 15
        buffer.drawRightString(width - 90, y, f"VAT ({quotation.vat_percentage}%):")
        buffer.drawRightString(width - 20, y, f"AED {quotation.vat_amount:.2f}")

        y -= 20
        buffer.drawRightString(width - 90, y, "Grand Total:")
        buffer.drawRightString(width - 20, y, f"AED {quotation.grand_total:.2f}")

        # Notes
        y -= 50
        buffer.setFont("Oswald", 9)
        buffer.drawString(x_margin, y, "Note:")
        buffer.drawString(x_margin + 40, y, "Please make payments to:")
        buffer.drawString(x_margin + 40, y - 15, "Bank: Abu Dhabi Commercial Bank (ADCB)")
        buffer.drawString(x_margin + 40, y - 30, "IBAN: AE390030013222731920001")
        buffer.drawString(x_margin + 40, y - 45, "Account Name: ULTRA PREMIUM AUTO CARE SERVICES LLC")

        buffer.showPage()
        buffer.save()
        return response
