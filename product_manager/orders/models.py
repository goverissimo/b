from django.db import models
from inventory.models import Product
from decimal import Decimal
from django.conf import settings
from django.db import transaction

class Order(models.Model):
    """
    Represents an order in the system.
    """
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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_orders')
    
    def save(self, *args, **kwargs):
        """
        Custom save method to handle inventory updates and profit calculations.
        """
        is_new = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            if is_new:
                self.update_inventory()
            
            self.total_price = self.calculate_total_price()
            self.profit = self.calculate_profit()
            super().save(update_fields=['total_price', 'profit'])

    def update_inventory(self, is_completed=True):
        """
        Update product inventory based on order status.
        """
        for item in self.items.all():
            product = item.product
            if is_completed:
                if product.quantity_in_stock >= item.quantity:
                    product.quantity_in_stock -= item.quantity
                    product.quantity_sold += item.quantity
                else:
                    raise ValueError(f"Not enough stock for product: {product.name}")
            else:
                product.quantity_in_stock += item.quantity
                product.quantity_sold -= item.quantity
            product.save()

    def calculate_total_price(self):
        """
        Calculate the total price of the order.
        """
        return sum(item.total_price for item in self.items.all())

    def calculate_profit(self):
        """
        Calculate the total profit of the order.
        """
        return sum(item.profit for item in self.items.all())

    def add_item(self, product, quantity, selling_price):
        """
        Add a new item to the order.
        """
        return OrderItem.objects.create(
            order=self,
            product=product,
            quantity=quantity,
            selling_price=selling_price
        )
    
    def complete_order(self):
        """
        Mark the order as completed and update inventory.
        """
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
    """
    Represents an item within an order.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        """
        Calculate the total price for this item.
        """
        return self.quantity * self.selling_price

    @property
    def profit(self):
        """
        Calculate the profit for this item.
        """
        return self.total_price - (self.product.purchase_price * self.quantity)

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure selling price is set and order is updated.
        """
        if not self.selling_price:
            self.selling_price = self.product.price
        super().save(*args, **kwargs)
        self.order.save()  # Update order totals