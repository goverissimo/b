from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(models.Model):
    """
    Represents a product in the inventory.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_bought = models.PositiveIntegerField(default=0)
    quantity_in_stock = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def calculate_profit(self):
        """
        Calculate the total profit for this product.
        """
        total_cost = self.purchase_price * Decimal(self.quantity_bought)
        total_revenue = self.price * Decimal(self.quantity_sold)
        return total_revenue - total_cost
    
    def is_available(self):
        """
        Check if the product is available in stock.
        """
        return self.quantity_in_stock > 0
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class PriceHistory(models.Model):
    """
    Represents the price history of a product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Price Histories"

    def __str__(self):
        return f"{self.product.name} - ${self.price} on {self.date.strftime('%Y-%m-%d')}"