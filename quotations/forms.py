# quotations/forms.py
from django import forms
from django.core.validators import RegexValidator
from django.forms.models import inlineformset_factory
from decimal import Decimal
import logging
from .models import Quotation, QuotationItem
from jobcards.models import JobCard
from customers.models import Customer
from vehicles.models import Vehicle

logger = logging.getLogger(__name__)

def create_quotation_item_formset(item_type='part'):
    """Create a formset for parts or services."""
    return inlineformset_factory(
        Quotation,
        QuotationItem,
        fields=['description', 'quantity', 'unit_price'],
        widgets={
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1',
                'data-item-type': item_type
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'value': '0.00',
                'data-item-type': item_type
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'data-item-type': item_type
            })
        },
        extra=0,
        formfield_callback=lambda field, **kwargs: {
            **kwargs,
            'initial': kwargs.get('initial', {'item_type': item_type})
        }
    )

# Create default formsets
PartsFormSet = create_quotation_item_formset('part')
ServicesFormSet = create_quotation_item_formset('service')

class QuotationForm(forms.ModelForm):
    include_vat = forms.BooleanField(
        required=False,
        label='Include 5% VAT',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        }),
        initial=True
    )
    
    discount_percentage = forms.DecimalField(
        required=False,
        initial=0,
        min_value=0,
        max_value=100,
        label='Discount %',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '100',
            'step': '1',
            'oninput': 'this.value = Math.min(100, Math.max(0, Math.round(this.value)));'
        })
    )
    
    class Meta:
        model = Quotation
        fields = ['include_vat', 'discount_percentage']
        
    def __init__(self, *args, **kwargs):
        self.jobcard = kwargs.pop('jobcard', None)
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.initial['include_vat'] = bool(self.instance.vat_percentage)
            self.initial['discount_percentage'] = self.instance.discount_percentage
    
    def clean(self):
        cleaned_data = super().clean()
        logger.info(f"Form data before cleaning: {cleaned_data}")
        
        # Convert checkbox to VAT percentage
        cleaned_data['vat_percentage'] = Decimal('5.0') if cleaned_data.get('include_vat') else Decimal('0.0')
        
        # Handle discount (validated in clean_discount_percentage)
        cleaned_data['discount_percentage'] = self.clean_discount_percentage()
        
        if self.errors:
            logger.error(f"Form errors: {self.errors}")
        
        logger.info(f"Form data after cleaning: {cleaned_data}")
        return cleaned_data
    
    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage')
        if discount is not None and str(discount).strip():
            try:
                discount = Decimal(str(round(float(discount))))
                if not (0 <= discount <= 100):
                    raise forms.ValidationError("Discount must be between 0 and 100 percent")
                return discount.quantize(Decimal('1'))
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing discount: {e}")
                raise forms.ValidationError("Please enter a valid number")
        return Decimal('0')

class CustomerForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[RegexValidator(r'^\+?[\d\s-]+$', 'Enter a valid phone number')]
    )
    
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'company', 'trn']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'trn': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VehicleForm(forms.ModelForm):
    vin = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[RegexValidator(r'^[A-HJ-NPR-Z0-9]{17}$', 'Enter a valid VIN')],
        required=False
    )
    
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'color', 'year', 'plate', 'vin', 'mileage']
        widgets = {
            'make': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'plate': forms.TextInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BaseQuotationItemFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.item_type = kwargs.pop('item_type', 'part')
        super().__init__(*args, **kwargs)
        self.min_num = 0  # Allow empty formsets
        self.validate_min = False

    def clean(self):
        super().clean()
        
        # Check for empty forms
        empty_forms = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                empty_forms += 1
                continue

        # If all forms are empty, that's fine - we'll handle it in the view
        if empty_forms == len(self.forms):
            return

        # Validate each non-empty form
        for i, form in enumerate(self.forms):
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
                
            self.validate_form_fields(form, i)

    def validate_form_fields(self, form, index):
        quantity = form.cleaned_data.get('quantity', 0)
        unit_price = form.cleaned_data.get('unit_price', 0)
        
        if quantity <= 0:
            form.add_error('quantity', 'Quantity must be greater than 0')
        if unit_price < 0:
            form.add_error('unit_price', 'Price cannot be negative')
        
        if form.errors:
            logger.error(f"Form {index} errors: {form.errors}")

def get_quotation_item_formset(extra=0, can_delete=True, **kwargs):
    """Factory function to create a properly configured formset"""
    return inlineformset_factory(
        Quotation,
        QuotationItem,
        formset=BaseQuotationItemFormSet,
        fields=['description', 'quantity', 'unit_price'],
        extra=extra,
        can_delete=can_delete,
        widgets={
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'style': 'resize: vertical; min-height: 28px;',
                'placeholder': 'Item description'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control text-center',
                'min': '1',
                'step': '1',
                'placeholder': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control text-end',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'DELETE': forms.HiddenInput(),
        }
    )

def create_quotation_formset(instance=None, data=None, jobcard=None, prefix='items'):
    """Create a formset with proper initial configuration"""
    FormSet = get_quotation_item_formset(extra=0 if not instance else 0)
    
    if not instance and jobcard:
        initial_data = [{
            'description': "",
            'quantity': 1,
            'unit_price': 0.00
        }]
        return FormSet(data, instance=instance, initial=initial_data, prefix=prefix)
    
    return FormSet(data, instance=instance, prefix=prefix)