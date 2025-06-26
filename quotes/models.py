from django.db import models
from jobcards.models import JobCard

class Quotation(models.Model):
    job_card = models.OneToOneField(JobCard, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    valid_until = models.DateField()
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    
    @property
    def total(self):
        return self.labor_cost + self.parts_cost
    
    def __str__(self):
        return f"Quote-{self.id}"

class Invoice(models.Model):
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"INV-{self.id}"