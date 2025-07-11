# jobcards/models.py
import datetime
from django.db import models
from customers.models import Customer
from vehicles.models import Vehicle

class JobCard(models.Model):
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

    def __str__(self):
        return f"JobCard #{self.id} - {self.customer}"
