from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    is_partner = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.manage_partner_status()

    def manage_partner_status(self):
        from partners.models import Partner
        if self.is_partner:
            Partner.objects.get_or_create(user=self)
        else:
            Partner.objects.filter(user=self).delete()

@receiver(post_save, sender=CustomUser)
def create_or_update_partner(sender, instance, created, **kwargs):
    instance.manage_partner_status()

# Note: The following two signal handlers are redundant with the above implementation
# and can be removed to avoid duplication.

# @receiver(post_save, sender=CustomUser)
# def create_partner(sender, instance, created, **kwargs):
#     if created and instance.is_partner:
#         from partners.models import Partner
#         Partner.objects.create(user=instance)

# @receiver(post_save, sender=CustomUser)
# def save_partner(sender, instance, **kwargs):
#     if instance.is_partner:
#         from partners.models import Partner
#         Partner.objects.get_or_create(user=instance)