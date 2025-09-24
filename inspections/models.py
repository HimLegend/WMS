# inspections/models.py
from django.db import models
from django.conf import settings
from jobcards.models import JobCard


class InspectionReport(models.Model):
    job_card = models.OneToOneField(JobCard, on_delete=models.CASCADE, related_name='inspection_report')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inspection Report for JobCard #{self.job_card.id}"

    @property
    def total_findings(self):
        return self.findings.count()

    @property
    def total_estimated_hours(self):
        return sum(f.time_required for f in self.findings.all())


class InspectionFinding(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    inspection = models.ForeignKey(InspectionReport, related_name="findings", on_delete=models.CASCADE)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    time_required = models.FloatField(default=1.0, help_text="Estimated time in hours")
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Finding #{self.id} – {self.severity.title()}"


class RequiredPart(models.Model):
    STATUS_CHOICES = [
        ('required', 'Required'),
        ('ordered', 'Ordered'),
        ('in_stock', 'In Stock'),
        ('installed', 'Installed'),
    ]

    finding = models.ForeignKey(InspectionFinding, related_name='parts', on_delete=models.CASCADE)
    part_number = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='required')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Part: {self.description}"


class RequiredConsumable(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('m', 'Meters'),
        ('cm', 'Centimeters'),
    ]

    finding = models.ForeignKey(InspectionFinding, related_name='consumables', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.FloatField(default=1)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Consumable: {self.name} ({self.quantity} {self.unit})"
