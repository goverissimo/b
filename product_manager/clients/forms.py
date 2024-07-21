from django import forms
from .models import Client
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['description', 'treatment_preferences', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))