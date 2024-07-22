from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import Partner, PartnerOrder
from accounts.models import CustomUser

@receiver(post_save, sender=Order)
def update_partner_profit(sender, instance, created, **kwargs):
    """
    Create a PartnerOrder when a new Order is created by a partner.
    """
    if created and instance.created_by:
        try:
            partner = Partner.objects.get(user=instance.created_by)
            partner_profit = instance.profit * (partner.profit_split_percentage / 100)
            PartnerOrder.objects.create(
                partner=partner,
                order=instance,
                partner_profit=partner_profit
            )
            partner.update_total_profit()
        except Partner.DoesNotExist:
            pass  # If the order creator is not a partner, do nothing

@receiver(post_save, sender=CustomUser)
def create_partner(sender, instance, created, **kwargs):
    """
    Create a Partner instance when a new CustomUser with is_partner=True is created.
    """
    if created and instance.is_partner:
        Partner.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_partner(sender, instance, **kwargs):
    """
    Ensure a Partner instance exists for CustomUsers with is_partner=True.
    """
    if instance.is_partner:
        Partner.objects.get_or_create(user=instance)