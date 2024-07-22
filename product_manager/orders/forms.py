from django import forms
from .models import Order, OrderItem
from inventory.models import Product

class OrderForm(forms.ModelForm):
    """
    Form for creating and editing Orders.
    """
    class Meta:
        model = Order
        fields = ['telegram_user_id', 'status', 'meeting_time']

class OrderItemForm(forms.ModelForm):
    """
    Form for creating and editing OrderItems.
    """
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'selling_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show products that are in stock
        self.fields['product'].queryset = Product.objects.filter(quantity_in_stock__gt=0)
        self.fields['selling_price'].widget.attrs['min'] = 0  # Ensure non-negative price

    def clean(self):
        """
        Custom validation to ensure ordered quantity doesn't exceed available stock.
        """
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            if quantity > product.quantity_in_stock:
                raise forms.ValidationError(f"Only {product.quantity_in_stock} units of {product.name} are available.")

        return cleaned_data

# Create a formset for OrderItems
OrderItemFormSet = forms.inlineformset_factory(
    Order, 
    OrderItem, 
    fields=['product', 'quantity', 'selling_price'], 
    extra=1,  # One extra empty form
    can_delete=True  # Allow deleting items
)