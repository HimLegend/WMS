from django.db import models


class Vehicle(models.Model):
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)  # Use string reference
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    vin = models.CharField(max_length=17, blank=True)
    license_plate = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model}"