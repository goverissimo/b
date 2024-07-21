from django.db import models
from django.core.exceptions import ValidationError

class DayOfWeek(models.TextChoices):
    MONDAY = 'MON', 'Monday'
    TUESDAY = 'TUE', 'Tuesday'
    WEDNESDAY = 'WED', 'Wednesday'
    THURSDAY = 'THU', 'Thursday'
    FRIDAY = 'FRI', 'Friday'
    SATURDAY = 'SAT', 'Saturday'
    SUNDAY = 'SUN', 'Sunday'

class AvailabilitySlot(models.Model):
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class AppointmentDuration(models.Model):
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=30)  # Add a default value

    def save(self, *args, **kwargs):
        if not self.pk and AppointmentDuration.objects.exists():
            # If you're trying to create a new object and one already exists,
            # just update the existing one.
            return AppointmentDuration.objects.update(duration=self.duration)
        return super(AppointmentDuration, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.duration} minutes"