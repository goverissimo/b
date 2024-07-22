from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
import logging

class Partner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profit_split_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username

    def calculate_total_profit(self):
        """Calculate total profit from completed orders."""
        return sum(order.partner_profit for order in self.orders.all() if order.order.status == 'completed')

    def update_total_profit(self):
        """Update the total profit for the partner."""
        self.total_profit = self.calculate_total_profit()
        self.save()

class PartnerOrder(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='orders')
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE)
    partner_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('partner', 'order')  # Ensures one PartnerOrder per Order

    def update_profit(self):
        """Update the profit for this partner order."""
        logging.info(f'Updating profit for order {self.order.id}')
        if self.order.status == 'completed':
            self.partner_profit = self.order.profit * (self.partner.profit_split_percentage / Decimal('100'))
        else:
            self.partner_profit = Decimal('0.00')
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.partner.update_total_profit()
    
    def __str__(self):
        return f"Partner: {self.partner.user.username}, Order: {self.order.id}"

# Signal handlers
@receiver(post_save, sender=Partner)
def update_user_partner_status(sender, instance, created, **kwargs):
    """Update user's partner status when a Partner instance is created."""
    if created:
        instance.user.is_partner = True
        instance.user.save()

@receiver(post_delete, sender=Partner)
def update_user_partner_status_on_delete(sender, instance, **kwargs):
    """Update user's partner status when a Partner instance is deleted."""
    instance.user.is_partner = False
    instance.user.save()

@receiver(post_save, sender=PartnerOrder)
@receiver(post_delete, sender=PartnerOrder)
def update_partner_total_profit(sender, instance, **kwargs):
    """Update partner's total profit when a PartnerOrder is saved or deleted."""
    instance.partner.update_total_profit()