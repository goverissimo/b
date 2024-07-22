from django import forms
from .models import Client
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ClientForm(forms.ModelForm):
    """
    Form for creating and updating Client instances.
    """
    class Meta:
        model = Client
        fields = ['description', 'treatment_preferences', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))

    def clean_telegram_id(self):
        telegram_id = self.cleaned_data.get('telegram_id')
        if telegram_id and telegram_id < 0:
            raise forms.ValidationError("Telegram ID must be a positive integer.")
        return telegram_id