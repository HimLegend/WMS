from django.db import models

class InventoryItem(models.Model):
    CATEGORIES = [
        ('part', 'Part'),
        ('consumable', 'Consumable'),
        ('tool', 'Tool'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.name} (Qty: {self.quantity})"