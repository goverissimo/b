from django.db import models
from django.contrib.auth.models import User

class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    telegram_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"Telegram User {self.telegram_id}"