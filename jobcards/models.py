from django.db import models
from vehicles.models import Vehicle
from django.contrib.auth import get_user_model

User = get_user_model()

class JobCard(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    assigned_technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField()
    customer_notes = models.TextField(blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    actual_completion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"JC-{self.id} ({self.vehicle})"