# quotations/forms.py

from django import forms
from .models import Quotation, QuotationItem
from django.forms.models import inlineformset_factory

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['vat_percentage', 'discount_percentage']

QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    fields=['description', 'quantity', 'unit_price'],
    extra=1,
    can_delete=True
)
