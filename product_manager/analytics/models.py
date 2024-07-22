from django.db import models

class AnalyticsConfig(models.Model):
    """
    Stores configuration settings for analytics.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = 'Analytics Configuration'
        verbose_name_plural = 'Analytics Configurations'