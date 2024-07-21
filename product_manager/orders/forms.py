
from django import forms
from .models import Order, OrderItem
from inventory.models import Product
from availability.utils import get_available_time_slots
from datetime import datetime, timedelta
import logging
class OrderForm(forms.ModelForm):
    meeting_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    meeting_time = forms.TimeField(widget=forms.Select(choices=[]))

    class Meta:
        model = Order
        fields = ['telegram_user_id', 'status', 'meeting_date', 'meeting_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'meeting_date' in self.data:
            try:
                date = datetime.strptime(self.data['meeting_date'], '%Y-%m-%d').date()
                logging.info(f"Generating time slots for {date}")
                time_slots = get_available_time_slots(date)
                self.fields['meeting_time'].widget.choices = [(slot.strftime('%H:%M'), slot.strftime('%I:%M %p')) for slot in time_slots]
                logging.info(f"Generated {len(self.fields['meeting_time'].widget.choices)} choices")
            except (ValueError, TypeError) as e:
                logging.error(f"Error generating time slots: {str(e)}")
                
    def clean(self):
        cleaned_data = super().clean()
        meeting_date = cleaned_data.get('meeting_date')
        meeting_time = cleaned_data.get('meeting_time')

        if meeting_date and meeting_time:
            cleaned_data['meeting_time'] = datetime.combine(meeting_date, meeting_time)

        return cleaned_data

class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)