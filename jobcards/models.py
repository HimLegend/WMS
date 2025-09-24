# jobcards/models.py
import datetime
from django.db import models
from customers.models import Customer
from vehicles.models import Vehicle

class ActiveJobCardManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(job_status__in=['ready_collection', 'delivered'])

class CompletedJobCardManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(job_status__in=['ready_collection', 'delivered'])

class JobCard(models.Model):
    """JobCard model with custom managers for Active and Completed jobs."""
    objects = models.Manager()  # Default manager for admin, migrations, and normal queries
    active = ActiveJobCardManager()
    completed = CompletedJobCardManager()

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='jobcards')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='jobcards')
    date = models.DateField(default=datetime.date.today)
    time = models.TimeField(default=datetime.time(0, 0))
    job_status = models.CharField(
        max_length=50,
        choices=[
            ('under_inspection', 'Under Inspection'),
            ('inspection_completed', 'Inspection Completed'),
            ('parts_sourcing', 'Parts Sourcing'),
            ('quote_issued', 'Quote Issued'),
            ('pending_approval', 'Pending Approval'),
            ('waiting_parts', 'Waiting Parts'),
            ('work_in_progress', 'Work in Progress'),
            ('work_completed', 'Work Completed'),
            ('under_testing', 'Under Testing'),
            ('ready_washing', 'Ready for Washing'),
            ('ready_collection', 'Ready for Collection'),
            ('delivered', 'Delivered'),
        ],
        default='under_inspection'
    )
    customer_comments = models.TextField(blank=True, null=True)
    workshop_comments = models.TextField(blank=True, null=True)
    required_jobs = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_default_quotation_description(self):
        """Generate default description for quotation items"""
        descriptions = []
        if self.required_jobs:
            descriptions.append(self.required_jobs)
        if self.workshop_comments:
            descriptions.append(f"Workshop notes: {self.workshop_comments}")
        return "\n".join(descriptions) or "Vehicle service and maintenance"

    def __str__(self):
        return f"JobCard #{self.id} - {self.customer}"

    def get_job_notes(self):
        return self.job_notes.all()


class JobNote(models.Model):
    jobcard = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='job_notes')
    note = models.TextField()

    def __str__(self):
        return f"Note for JobCard #{self.jobcard.id}: {self.note[:30]}"
