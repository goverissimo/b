from django.contrib import admin
from .models import AvailabilitySlot, AppointmentDuration

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)

@admin.register(AppointmentDuration)
class AppointmentDurationAdmin(admin.ModelAdmin):
    list_display = ('duration',)