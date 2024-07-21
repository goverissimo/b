from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_bought = models.PositiveIntegerField(default=0)
    quantity_in_stock = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def calculate_profit(self):
        total_cost = self.purchase_price * Decimal(self.quantity_bought)
        total_revenue = self.price * Decimal(self.quantity_sold)
        return total_revenue - total_cost
    
    def is_available(self):
        return self.quantity_in_stock > 0
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']