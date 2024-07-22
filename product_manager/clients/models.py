from django.db import models
from django.core.exceptions import ValidationError

class Client(models.Model):
    """
    Represents a client in the system.
    """
    nickname = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=200, blank=True)
    telegram_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    treatment_preferences = models.TextField(blank=True)
    address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.get_display_name()

    class Meta:
        ordering = ['nickname', 'name', 'telegram_id']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def clean(self):
        if not self.nickname and not self.name:
            raise ValidationError("Either nickname or name must be provided.")

    def get_display_name(self):
        """
        Returns the display name for the client.
        """
        if self.nickname:
            return self.nickname
        elif self.name:
            return self.name
        else:
            return f"Client {self.telegram_id}"

    def get_full_name(self):
        """
        Returns a string representation of the client's full name.
        """
        if self.name:
            return self.name
        return self.get_display_name()

    def get_short_name(self):
        """
        Returns a short string representation of the client.
        """
        return self.get_display_name()