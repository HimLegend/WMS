from django.db import models
from jobcards.models import JobCard

class InspectionReport(models.Model):
    job_card = models.OneToOneField(JobCard, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    findings = models.TextField()
    recommendations = models.TextField()
    inspector_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Inspection for {self.job_card}"