from django.db import models
from django.utils import timezone
from orders.models import Order

class Expense(models.Model):
    """
    Represents an expense in the budget system.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - ${self.amount}"

    class Meta:
        ordering = ['-date']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

class Income(models.Model):
    """
    Represents income from a completed order.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Income from Order #{self.order.id} - ${self.amount}"

    class Meta:
        ordering = ['-date']
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'