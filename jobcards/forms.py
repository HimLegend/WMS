# jobcards/forms.py
from django import forms
from .models import JobCard, Customer, Vehicle

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
        fields = [
            "customer_comments", "workshop_comments", "required_jobs",
            "date", "time", "job_status"
        ]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
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

        self.request = request  # for saving multiple input lines later

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Create or update customer
        customer, _ = Customer.objects.get_or_create(
            name=self.cleaned_data["customer_name"],
            phone=self.cleaned_data["customer_phone"],
            defaults={
                "email": self.cleaned_data["customer_email"],
                "company": self.cleaned_data["customer_company"],
                "trn": self.cleaned_data["customer_trn"],
            }
        )
        instance.customer = customer

        # Create or update vehicle
        vehicle, created = Vehicle.objects.get_or_create(
            plate=self.cleaned_data["vehicle_plate"],
            defaults={
                "make": self.cleaned_data["vehicle_make"],
                "model": self.cleaned_data["vehicle_model"],
                "color": self.cleaned_data["vehicle_color"],
                "year": self.cleaned_data["vehicle_year"],
                "vin": self.cleaned_data["vehicle_vin"],
                "mileage": self.cleaned_data["vehicle_mileage"],
                "customer": customer,
            }
        )
        if not created and vehicle.customer is None:
            vehicle.customer = customer
            vehicle.save()

        instance.vehicle = vehicle

        # Handle dynamic item lists from POST
        if self.request:
            instance.required_jobs = "\n".join(self.request.POST.getlist("required_jobs[]"))
            instance.customer_comments = "\n".join(self.request.POST.getlist("customer_comments[]"))
            instance.workshop_comments = "\n".join(self.request.POST.getlist("workshop_comments[]"))

        if commit:
            instance.save()

        return instance
