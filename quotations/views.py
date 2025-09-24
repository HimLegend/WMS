# quotations/views.py
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from decimal import Decimal
import logging

from .models import Quotation, QuotationItem
from .forms import *
from jobcards.models import JobCard

logger = logging.getLogger(__name__)

class SelectJobcardView(ListView):
    """List active jobcards without existing quotation for selection."""
    model = JobCard
    template_name = 'quotations/select_jobcard.html'
    context_object_name = 'jobcards'

    def get_queryset(self):
        return JobCard.active.filter(quotations__isnull=True).order_by('-date', '-id')


class QuotationListView(ListView):
    model = Quotation
    template_name = 'quotations/list.html'
    context_object_name = 'quotations'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobcards'] = JobCard.active.all().order_by('-date', '-id')
        return context


class QuotationDetailView(DetailView):
    model = Quotation
    template_name = 'quotations/detail.html'
    context_object_name = 'quotation'

class QuotationCreateView(CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.jobcard = get_object_or_404(JobCard, pk=kwargs['jobcard_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['jobcard'] = self.jobcard
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobcard'] = self.jobcard

        # For create view, we don't have an instance yet
        instance = None
        
        if self.request.method == 'POST':
            context['parts_formset'] = PartsFormSet(
                self.request.POST,
                prefix='parts',
                instance=instance
            )
            context['services_formset'] = ServicesFormSet(
                self.request.POST,
                prefix='services',
                instance=instance
            )
        else:
            initial_data = [{
                'description': '',
                'quantity': 1,
                'unit_price': 0
            }]
            
            parts_queryset = QuotationItem.objects.none()
            services_queryset = QuotationItem.objects.none()
            
            # For create view, we don't have any items yet
            context['parts_formset'] = PartsFormSet(
                prefix='parts',
                instance=instance,
                queryset=parts_queryset,
                initial=initial_data if not instance else None
            )
            
            context['services_formset'] = ServicesFormSet(
                prefix='services',
                instance=instance,
                queryset=services_queryset,
                initial=initial_data if not instance else None
            )

        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        
        # Initialize both formsets
        parts_formset = PartsFormSet(
            data=request.POST,
            prefix='parts',
            instance=self.object if hasattr(self, 'object') else None
        )
        
        services_formset = ServicesFormSet(
            data=request.POST,
            prefix='services',
            instance=self.object if hasattr(self, 'object') else None
        )

        # Handle form submission
        if form.is_valid() and parts_formset.is_valid() and services_formset.is_valid():
            return self.form_valid(form, parts_formset, services_formset)
        else:
            return self.form_invalid(form, parts_formset, services_formset)

    def form_valid(self, form, parts_formset, services_formset):
        try:
            with transaction.atomic():
                # Set the jobcard before saving
                self.object = form.save(commit=False)
                self.object.jobcard = self.jobcard
                self.object.save()

                # Save parts
                parts_instances = parts_formset.save(commit=False)
                for instance in parts_instances:
                    instance.quotation = self.object
                    instance.item_type = 'part'
                    instance.save()

                # Save services
                services_instances = services_formset.save(commit=False)
                for instance in services_instances:
                    instance.quotation = self.object
                    instance.item_type = 'service'
                    instance.save()

                # Delete any marked for deletion
                for obj in parts_formset.deleted_objects:
                    obj.delete()
                for obj in services_formset.deleted_objects:
                    obj.delete()

                messages.success(self.request, 'Quotation created successfully!')
                return redirect('quotations:detail', pk=self.object.pk)

        except Exception as e:
            logger.error(f"Error creating quotation: {str(e)}", exc_info=True)
            messages.error(self.request, 'An error occurred while creating the quotation.')
            return self.form_invalid(form, parts_formset, services_formset)

    def form_invalid(self, form, parts_formset, services_formset):
        # Log form errors
        logger.error(f"Form errors: {form.errors}")
        
        # Add form errors to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        
        # Add parts formset errors to messages
        for i, form_in_formset in enumerate(parts_formset):
            if form_in_formset.errors:
                for field, errors in form_in_formset.errors.items():
                    for error in errors:
                        messages.error(
                            self.request, 
                            f"Parts - Row {i + 1} - {form_in_formset.fields[field].label or field}: {error}"
                        )
        
        # Add services formset errors to messages
        for i, form_in_formset in enumerate(services_formset):
            if form_in_formset.errors:
                for field, errors in form_in_formset.errors.items():
                    for error in errors:
                        messages.error(
                            self.request, 
                            f"Services - Row {i + 1} - {form_in_formset.fields[field].label or field}: {error}"
                        )
        
        # Return the response with the invalid forms
        return self.render_to_response(
            self.get_context_data(
                form=form,
                parts_formset=parts_formset,
                services_formset=services_formset
            )
        )

class QuotationUpdateView(UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobcard'] = self.object.jobcard

        if self.request.POST:
            context['formset'] = QuotationItemFormSet(
                data=self.request.POST,
                instance=self.object,
                prefix='items'
            )
        else:
            context['formset'] = QuotationItemFormSet(
                instance=self.object,
                prefix='items'
            )

        # Provide totals for display if needed
        context.update(self._calculate_totals(self.object))
        return context

    def _calculate_totals(self, quotation):
        return {
            'subtotal': quotation.subtotal,
            'vat_amount': quotation.vat_amount,
            'discount_amount': quotation.discount_amount,
            'grand_total': quotation.grand_total
        }

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = QuotationItemFormSet(
            data=request.POST,
            instance=self.object,
            prefix='items'
        )

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    formset.instance = self.object
                    formset.save()
                    messages.success(request, 'Quotation updated successfully.')
                    return redirect('quotation_detail', pk=self.object.pk)
            except Exception as e:
                logger.error(f"Error updating quotation: {str(e)}")
                messages.error(request, f'Error updating quotation: {str(e)}')
                # Fall through to re-render form with errors

        # If form or formset invalid, re-render the page with errors
        context = self.get_context_data(form=form)
        context['formset'] = formset
        return self.render_to_response(context)

class QuotationPDFView(View):
    """Generate PDF version of quotation"""
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    
    # Register fonts once when class loads
    pdfmetrics.registerFont(TTFont('Oswald-Bold', os.path.join(font_dir, 'Oswald-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Oswald', os.path.join(font_dir, 'Oswald-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Poppins-Bold', os.path.join(font_dir, 'Poppins-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Poppins', os.path.join(font_dir, 'Poppins-Regular.ttf')))

    def get(self, request, pk, *args, **kwargs):
        quotation = get_object_or_404(Quotation, pk=pk)
        jobcard = quotation.jobcard
        customer = jobcard.customer
        vehicle = jobcard.vehicle

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Quotation-{quotation.quotation_number}.pdf'

        buffer = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        x_margin = 30
        y = height - 30

        self._draw_header(buffer, width, x_margin, y, quotation)
        y -= 80

        self._draw_customer_info(buffer, x_margin, y, customer)
        self._draw_vehicle_info(buffer, width, y, vehicle)
        y -= 110

        self._draw_items_table(buffer, width, x_margin, y, quotation)
        
        buffer.showPage()
        buffer.save()
        return response

    def _draw_header(self, buffer, width, x_margin, y, quotation):
        """Draw company header and quotation info"""
        # Logo
        logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
        if os.path.exists(logo_path):
            buffer.drawImage(logo_path, x_margin, y - 50, width=100, height=40, mask='auto')

        # Company Info
        buffer.setFont("Oswald-Bold", 14)
        buffer.drawString(x_margin + 120, y, "Ultra Premium Auto Care Services LLC")
        buffer.setFont("Oswald", 9)
        buffer.drawString(x_margin + 120, y - 15, "Dubai, UAE")
        buffer.drawString(x_margin + 120, y - 30, "Phone: +97148818838 | info@ultrapremium.vip")
        buffer.drawString(x_margin + 120, y - 45, "TRN: 100541878800003")

        # Quotation Info
        buffer.setFont("Oswald-Bold", 12)
        buffer.drawString(x_margin, y - 80, f"QUOTATION #: {quotation.quotation_number}")
        buffer.drawString(width - 150, y - 80, f"Date: {quotation.date_created.strftime('%Y-%m-%d')}")

    def _draw_customer_info(self, buffer, x_margin, y, customer):
        """Draw customer information section"""
        buffer.setFont("Poppins-Bold", 10)
        buffer.drawString(x_margin, y, "BILL TO")
        buffer.setFont("Poppins", 9)
        buffer.drawString(x_margin, y - 15, f"Name: {customer.name}")
        buffer.drawString(x_margin, y - 30, f"Phone: {customer.phone}")
        buffer.drawString(x_margin, y - 45, f"Company: {customer.company or '-'}")
        buffer.drawString(x_margin, y - 60, f"TRN: {customer.trn or '-'}")

    def _draw_vehicle_info(self, buffer, width, y, vehicle):
        """Draw vehicle information section"""
        buffer.setFont("Poppins-Bold", 10)
        buffer.drawString(width / 2, y, "VEHICLE INFO")
        buffer.setFont("Poppins", 9)
        buffer.drawString(width / 2, y - 15, f"Make: {vehicle.make}")
        buffer.drawString(width / 2, y - 30, f"Model: {vehicle.model}")
        buffer.drawString(width / 2, y - 45, f"Year: {vehicle.year}")
        buffer.drawString(width / 2, y - 60, f"Plate: {vehicle.plate}")
        buffer.drawString(width / 2, y - 75, f"VIN: {vehicle.vin or '-'}")
        buffer.drawString(width / 2, y - 90, f"Mileage: {vehicle.mileage or '-'} km")

    def _draw_items_table(self, buffer, width, x_margin, y, quotation):
        """Draw items table and totals"""
        # Table Headers
        buffer.setFont("Poppins-Bold", 10)
        buffer.drawString(x_margin, y, "Qty")
        buffer.drawString(x_margin + 50, y, "Description")
        buffer.drawString(width - 150, y, "Unit Price")
        buffer.drawString(width - 80, y, "Amount")
        y -= 15

        # Table Rows
        buffer.setFont("Poppins", 9)
        for item in quotation.items.all():
            if y < 100:  # Check for page break
                buffer.showPage()
                y = height - 100
            buffer.drawString(x_margin, y, str(item.quantity))
            buffer.drawString(x_margin + 50, y, item.description)
            buffer.drawRightString(width - 90, y, f"AED {item.unit_price:.2f}")
            buffer.drawRightString(width - 20, y, f"AED {item.line_total:.2f}")
            y -= 15

        # Totals
        y -= 15
        buffer.setFont("Poppins-Bold", 10)
        self._draw_total_row(buffer, width, y, "Subtotal:", f"AED {quotation.subtotal:.2f}")
        
        if quotation.discount_percentage > 0:
            y -= 15
            self._draw_total_row(
                buffer, width, y, 
                f"Discount ({quotation.discount_percentage}%):", 
                f"-AED {quotation.discount_amount:.2f}"
            )

        if quotation.vat_percentage > 0:
            y -= 15
            self._draw_total_row(
                buffer, width, y,
                f"VAT ({quotation.vat_percentage}%):",
                f"AED {quotation.vat_amount:.2f}"
            )

        y -= 20
        self._draw_total_row(buffer, width, y, "Grand Total:", f"AED {quotation.grand_total:.2f}")

        # Payment Info
        y -= 50
        buffer.setFont("Oswald", 9)
        buffer.drawString(x_margin, y, "Note:")
        buffer.drawString(x_margin + 40, y, "Please make payments to:")
        buffer.drawString(x_margin + 40, y - 15, "Bank: Abu Dhabi Commercial Bank (ADCB)")
        buffer.drawString(x_margin + 40, y - 30, "IBAN: AE390030013222731920001")
        buffer.drawString(x_margin + 40, y - 45, "Account Name: ULTRA PREMIUM AUTO CARE SERVICES LLC")

    def _draw_total_row(self, buffer, width, y, label, value):
        """Helper to draw a total row with consistent formatting"""
        buffer.drawRightString(width - 90, y, label)
        buffer.drawRightString(width - 20, y, value)