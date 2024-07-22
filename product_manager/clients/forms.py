from django import forms
from .models import Client
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Fieldset, Submit
from crispy_forms.bootstrap import FormActions
class ClientForm(forms.ModelForm):
    """
    Form for creating and updating Client instances.
    """
    class Meta:
        model = Client
        fields = ['nickname', 'name', 'telegram_id', 'description', 'treatment_preferences', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Client Information',
                'nickname',
                'name',
                'telegram_id',
            ),
            Fieldset(
                'Additional Information',
                'description',
                'treatment_preferences',
                'address',
            ),
            FormActions(
                Submit('submit', 'Save', css_class='btn-primary')
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        nickname = cleaned_data.get('nickname')
        name = cleaned_data.get('name')
        
        if not nickname and not name:
            raise forms.ValidationError("Either nickname or name must be provided.")
        
        return cleaned_data

    def clean_telegram_id(self):
        telegram_id = self.cleaned_data.get('telegram_id')
        if telegram_id and telegram_id < 0:
            raise forms.ValidationError("Telegram ID must be a positive integer.")
        return telegram_id