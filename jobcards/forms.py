from django import forms
from .models import JobCard

class JobCardForm(forms.ModelForm):
    class Meta:
        model = JobCard
        fields = [
            'vehicle',
            'assigned_technician',
            'status',
            'description',
            'customer_notes',
            'estimated_completion'
        ]
        widgets = {
            'estimated_completion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'customer_notes': forms.Textarea(attrs={'rows': 3}),
        }