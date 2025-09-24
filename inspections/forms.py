from django import forms
from django.forms import inlineformset_factory
from .models import InspectionReport, InspectionFinding, RequiredPart, RequiredConsumable


class InspectionReportForm(forms.ModelForm):
    class Meta:
        model = InspectionReport
        # Exclude fields set automatically or via code, keep only editable if any
        fields = []
        # Or if you want user to see job_card, use:
        # fields = ['job_card']

class InspectionFindingForm(forms.ModelForm):
    class Meta:
        model = InspectionFinding
        fields = ['description', 'severity', 'time_required', 'remarks']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'time_required': forms.NumberInput(attrs={'step': 0.1, 'class': 'form-control', 'min': 0}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
        labels = {
            'time_required': 'Estimated Time (hours)',
        }

class RequiredPartForm(forms.ModelForm):
    class Meta:
        model = RequiredPart
        fields = ['part_number', 'description', 'quantity', 'status', 'notes']
        widgets = {
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class RequiredConsumableForm(forms.ModelForm):
    class Meta:
        model = RequiredConsumable
        fields = ['name', 'quantity', 'unit', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.01, 'step': 0.01}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


FindingFormSet = inlineformset_factory(
    InspectionReport,
    InspectionFinding,
    form=InspectionFindingForm,
    extra=1,
    can_delete=True
)

PartFormSet = inlineformset_factory(
    InspectionFinding,
    RequiredPart,
    form=RequiredPartForm,
    extra=1,
    can_delete=True
)

ConsumableFormSet = inlineformset_factory(
    InspectionFinding,
    RequiredConsumable,
    form=RequiredConsumableForm,
    extra=1,
    can_delete=True
)
