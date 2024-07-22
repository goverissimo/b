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
    Represents income from a completed order or paid debt.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        source = f"Order #{self.order.id}" if self.order else "Debt payment"
        return f"Income from {source} - ${self.amount}"

    class Meta:
        ordering = ['-date']
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'
        
class Debt(models.Model):
    """
    Represents a debt in the budget system.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateField(default=timezone.now)
    date_paid = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    expense = models.OneToOneField(Expense, on_delete=models.SET_NULL, null=True, blank=True, related_name='debt')
    income = models.OneToOneField(Income, on_delete=models.SET_NULL, null=True, blank=True, related_name='debt')

    def __str__(self):
        return f"{self.name} - ${self.amount}"

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Debt'
        verbose_name_plural = 'Debts'