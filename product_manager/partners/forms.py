from django import forms
from orders.models import Order, OrderItem
from inventory.models import Product

from django import forms

from django import forms
from orders.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['telegram_user_id', 'status', 'meeting_time']
        widgets = {
            'meeting_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'pending'


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'selling_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(quantity_in_stock__gt=0)
        self.fields['selling_price'].widget.attrs['min'] = 0

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            if quantity > product.quantity_in_stock:
                raise forms.ValidationError(f"Only {product.quantity_in_stock} units of {product.name} are available.")

        return cleaned_data