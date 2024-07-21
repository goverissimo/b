# inventory/forms.py
from django import forms
from .models import Product, PriceHistory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'purchase_price', 'quantity_bought', 'quantity_in_stock', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
            # Create a new PriceHistory entry if the price has changed
            if self.has_changed() and 'price' in self.changed_data:
                PriceHistory.objects.create(product=product, price=product.price)
        return product
