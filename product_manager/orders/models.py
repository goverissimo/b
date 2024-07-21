from django.db import models
from inventory.models import Product
from decimal import Decimal

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_user_id = models.IntegerField()
    STATUS_CHOICES = [
        ('cart', 'Cart'),
        ('pending_appointment', 'Pending Appointment'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')
    meeting_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    
    def calculate_profit(self):
        profit = Decimal('0.00')
        for item in self.items.all():
            product = item.product
            item_cost = product.purchase_price * Decimal(item.quantity)
            item_revenue = item.price * Decimal(item.quantity)
            item_profit = item_revenue - item_cost
            profit += item_profit
        return profit


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.profit = self.calculate_profit()
        super().save(update_fields=['profit'])
    
    def complete_order(self):
        for item in self.items.all():
            product = item.product
            product.quantity_in_stock -= item.quantity
            product.quantity_sold += item.quantity
            product.save()
        
        self.status = 'completed'
        self.save()
        
    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
