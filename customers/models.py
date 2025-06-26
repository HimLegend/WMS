from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    # If you need vehicle access:
    @property
    def vehicles(self):
        from vehicles.models import Vehicle
        return Vehicle.objects.filter(customer=self)