# jobcards/forms.py
import logging
from django import forms
from django.utils import timezone
from .models import JobCard, Customer, Vehicle

import sys
logger = logging.getLogger("jobcard_debug")
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    logger.addHandler(handler)
logger.setLevel(logging.WARNING)

class JobCardModelForm(forms.ModelForm):
    # Inline Customer fields
    customer_name = forms.CharField(max_length=100, label="Customer Name")
    customer_phone = forms.CharField(max_length=20, label="Phone")
    customer_email = forms.EmailField(required=False, label="Email")
    customer_company = forms.CharField(max_length=150, required=False, label="Company Name")
    customer_trn = forms.CharField(max_length=20, required=False, label="TRN")

    # Inline Vehicle fields
    vehicle_make = forms.CharField(max_length=50)
    vehicle_model = forms.CharField(max_length=50)
    vehicle_color = forms.CharField(max_length=30)
    vehicle_year = forms.IntegerField()
    vehicle_plate = forms.CharField(max_length=20, label="Plate Number")
    vehicle_vin = forms.CharField(max_length=50, required=False)
    vehicle_mileage = forms.IntegerField()

    class Meta:
        model = JobCard
        exclude = ['customer', 'vehicle']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["customer_name"].initial = self.instance.customer.name
            self.fields["customer_phone"].initial = self.instance.customer.phone
            self.fields["customer_email"].initial = self.instance.customer.email
            self.fields["customer_company"].initial = self.instance.customer.company
            self.fields["customer_trn"].initial = self.instance.customer.trn

            self.fields["vehicle_make"].initial = self.instance.vehicle.make
            self.fields["vehicle_model"].initial = self.instance.vehicle.model
            self.fields["vehicle_color"].initial = self.instance.vehicle.color
            self.fields["vehicle_year"].initial = self.instance.vehicle.year
            self.fields["vehicle_plate"].initial = self.instance.vehicle.plate
            self.fields["vehicle_vin"].initial = self.instance.vehicle.vin
            self.fields["vehicle_mileage"].initial = self.instance.vehicle.mileage
        else:
            # Prefill date/time with current values
            now = timezone.localtime()
            self.fields["date"].initial = now.date()
            self.fields["time"].initial = now.strftime("%H:%M")
            # Prefill from GET params if available
            if self.request:
                customer_id = self.request.GET.get("customer")
                vehicle_id = self.request.GET.get("vehicle")

                from .models import Customer, Vehicle
                if customer_id:
                    try:
                        customer = Customer.objects.get(pk=customer_id)
                        self.fields["customer_name"].initial = customer.name
                        self.fields["customer_phone"].initial = customer.phone
                        self.fields["customer_email"].initial = customer.email
                        self.fields["customer_company"].initial = customer.company
                        self.fields["customer_trn"].initial = customer.trn
                    except Customer.DoesNotExist:
                        pass
                if vehicle_id:
                    try:
                        vehicle = Vehicle.objects.get(pk=vehicle_id)
                        self.fields["vehicle_make"].initial = vehicle.make
                        self.fields["vehicle_model"].initial = vehicle.model
                        self.fields["vehicle_color"].initial = vehicle.color
                        self.fields["vehicle_year"].initial = vehicle.year
                        self.fields["vehicle_plate"].initial = vehicle.plate
                        self.fields["vehicle_vin"].initial = vehicle.vin
                        self.fields["vehicle_mileage"].initial = vehicle.mileage
                        # If customer not set by param, use vehicle's customer
                        if not customer_id and vehicle.customer:
                            self.fields["customer_name"].initial = vehicle.customer.name
                            self.fields["customer_phone"].initial = vehicle.customer.phone
                            self.fields["customer_email"].initial = vehicle.customer.email
                            self.fields["customer_company"].initial = vehicle.customer.company
                            self.fields["customer_trn"].initial = vehicle.customer.trn
                    except Vehicle.DoesNotExist:
                        pass

    def save(self, commit=True):
        # Use request to get dynamic job details fields
        instance = super().save(commit=False)

        # Fix: On update, modify the existing customer; on create, use get_or_create
        if self.instance.pk and self.instance.customer:
            # Editing: update the linked customer
            customer = self.instance.customer
            customer.name = self.cleaned_data["customer_name"]
            customer.phone = self.cleaned_data["customer_phone"]
            customer.email = self.cleaned_data["customer_email"]
            customer.company = self.cleaned_data["customer_company"]
            customer.trn = self.cleaned_data["customer_trn"]
            customer.save()
            instance.customer = customer
        else:
            # Creating: get or create customer
            customer, created = Customer.objects.get_or_create(
                name=self.cleaned_data["customer_name"],
                phone=self.cleaned_data["customer_phone"]
            )
            customer.email = self.cleaned_data["customer_email"]
            customer.company = self.cleaned_data["customer_company"]
            customer.trn = self.cleaned_data["customer_trn"]
            customer.save()
            instance.customer = customer

        # Update or create vehicle
        vehicle, created = Vehicle.objects.get_or_create(
            plate=self.cleaned_data["vehicle_plate"],
            defaults={
                "make": self.cleaned_data["vehicle_make"],
                "model": self.cleaned_data["vehicle_model"],
                "color": self.cleaned_data["vehicle_color"],
                "year": int(self.cleaned_data["vehicle_year"]),
                "vin": self.cleaned_data["vehicle_vin"],
                "mileage": int(self.cleaned_data["vehicle_mileage"]),
                "customer": customer,
            }
        )
        # Update fields in case of edit
        vehicle.make = self.cleaned_data["vehicle_make"]
        vehicle.model = self.cleaned_data["vehicle_model"]
        vehicle.color = self.cleaned_data["vehicle_color"]
        vehicle.year = int(self.cleaned_data["vehicle_year"])
        vehicle.vin = self.cleaned_data["vehicle_vin"]
        vehicle.mileage = int(self.cleaned_data["vehicle_mileage"])
        vehicle.customer = customer
        vehicle.save()
        instance.vehicle = vehicle

        # Handle dynamic inputs from the form
        # Robustly handle job details fields
        def _get_list_or_cleaned(field):
            vals = []
            if self.request:
                vals = self.request.POST.getlist(f"{field}[]")
            if vals:
                return "\n".join([v for v in vals if v.strip()])
            # fallback to cleaned_data (single value)
            return self.cleaned_data.get(field, "") or ""

        instance.required_jobs = _get_list_or_cleaned("required_jobs")
        instance.customer_comments = _get_list_or_cleaned("customer_comments")
        instance.workshop_comments = _get_list_or_cleaned("workshop_comments")

        if commit:
            instance.save()

        return instance
