from django.db import models

class Client(models.Model):
    telegram_id = models.PositiveIntegerField(unique=True)
    description = models.TextField(blank=True)
    treatment_preferences = models.TextField(blank=True)
    address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Client {self.telegram_id}"