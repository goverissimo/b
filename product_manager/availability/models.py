from django.db import models
from django.core.exceptions import ValidationError

class DayOfWeek(models.TextChoices):
    """
    Choices for days of the week.
    """
    MONDAY = 'MON', 'Monday'
    TUESDAY = 'TUE', 'Tuesday'
    WEDNESDAY = 'WED', 'Wednesday'
    THURSDAY = 'THU', 'Thursday'
    FRIDAY = 'FRI', 'Friday'
    SATURDAY = 'SAT', 'Saturday'
    SUNDAY = 'SUN', 'Sunday'

class AvailabilitySlot(models.Model):
    """
    Represents an availability time slot.
    """
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        """
        Validate that end time is after start time.
        """
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Availability Slot'
        verbose_name_plural = 'Availability Slots'

class AppointmentDuration(models.Model):
    """
    Represents the duration of appointments.
    """
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=30)

    def save(self, *args, **kwargs):
        """
        Ensure only one instance of AppointmentDuration exists.
        """
        if not self.pk and AppointmentDuration.objects.exists():
            return AppointmentDuration.objects.update(duration=self.duration)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.duration} minutes"

    class Meta:
        verbose_name = 'Appointment Duration'
        verbose_name_plural = 'Appointment Durations'