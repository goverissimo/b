from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import Income

@receiver(post_save, sender=Order)
def create_income_for_completed_order(sender, instance, created, **kwargs):
    """
    Create an Income instance when an Order is marked as completed.
    """
    if instance.status == 'completed' and not Income.objects.filter(order=instance).exists():
        Income.objects.create(order=instance, amount=instance.total_price)