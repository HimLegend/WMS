# quotations/models.py

import datetime
from django.db import models
from decimal import Decimal
from jobcards.models import JobCard
from django.utils import timezone
from decimal import Decimal, InvalidOperation


class Quotation(models.Model):
    jobcard = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name="quotations")
    quotation_number = models.CharField(max_length=20, unique=True, blank=True)
    date_created = models.DateField(default=datetime.date.today)
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        total = Decimal('0')
        for item in self.items.all():
            if hasattr(item, 'total'):
                total += Decimal(str(item.total))
        return total.quantize(Decimal('0.01'))

    @property
    def discount_amount(self):
        discount = (self.subtotal * Decimal(str(self.discount_percentage))) / Decimal('100')
        return discount.quantize(Decimal('0.01'))

    @property
    def vat_amount(self):
        subtotal_after_discount = self.subtotal - self.discount_amount
        vat = (subtotal_after_discount * Decimal(str(self.vat_percentage))) / Decimal('100')
        return vat.quantize(Decimal('0.01'))

    @property
    def grand_total(self):
        total = self.subtotal - self.discount_amount + self.vat_amount
        return total.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            today = timezone.now().strftime('%y%m%d')
            prefix = f"Q{today}"
            count_today = Quotation.objects.filter(quotation_number__startswith=prefix).count() + 1
            serial = f"{count_today:02d}"  # formats to 01, 02, etc.
            self.quotation_number = f"{prefix}-{serial}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.quotation_number

    class Meta:
        verbose_name_plural = "Quotations"


class QuotationItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('part', 'Part'),
        ('service', 'Service'),
    ]
    
    quotation = models.ForeignKey('Quotation', on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='part')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        try:
            qty = Decimal(str(self.quantity or 0))
            price = self.unit_price or Decimal('0.00')
            return (qty * price).quantize(Decimal('0.01'))
        except (InvalidOperation, TypeError):
            return Decimal('0.00')

    @property
    def total(self):
        return self.line_total

    def __str__(self):
        return self.description

    class Meta:
        verbose_name_plural = "Quotation Items"
