from django.db import models
from customers.models import Customer

class Vehicle(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="vehicles")
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    year = models.PositiveIntegerField()
    plate = models.CharField(help_text="number + code + city", max_length=20, unique=True)
    vin = models.CharField(help_text="16 digits", max_length=50, blank=True, null=True)
    mileage = models.PositiveIntegerField(help_text="Enter current mileage in KM", null=True, blank=True)


    def __str__(self):
        return f"{self.make} {self.model} ({self.plate})"
