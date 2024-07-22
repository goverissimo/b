from django import forms
from .models import AppointmentDuration

class AppointmentDurationForm(forms.ModelForm):
    """
    Form for updating the appointment duration.
    """
    class Meta:
        model = AppointmentDuration
        fields = ['duration']
        widgets = {
            'duration': forms.NumberInput(attrs={'min': 1, 'max': 120})  # 2h max
        }