# Add this form to your forms.py file
from django import forms
from .models import AppointmentDuration

class AppointmentDurationForm(forms.ModelForm):
    class Meta:
        model = AppointmentDuration
        fields = ['duration']