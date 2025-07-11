# customers/models.py
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    company = models.CharField(max_length=150, blank=True, null=True)
    trn = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.company if self.company else self.name
