from django.db import models

class Client(models.Model):
    """
    Represents a client in the system.
    """
    telegram_id = models.PositiveIntegerField(unique=True)
    description = models.TextField(blank=True)
    treatment_preferences = models.TextField(blank=True)
    address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Client {self.telegram_id}"

    class Meta:
        ordering = ['telegram_id']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def get_full_name(self):
        """
        Returns a string representation of the client's full name.
        This method should be implemented if you add name fields to the model.
        """
        return f"Client {self.telegram_id}"

    def get_short_name(self):
        """
        Returns a short string representation of the client.
        """
        return str(self.telegram_id)