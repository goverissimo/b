from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Product, PriceHistory
from .forms import ProductForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
class ProductListView(AdminRequiredMixin, ListView):
    """
    Display a list of products with search functionality.
    """
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ProductCreateView(AdminRequiredMixin, CreateView):
    """
    Create a new product.
    """
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product-list')

class ProductUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update an existing product.
    """
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.quantity_sold = self.object.quantity_bought - self.object.quantity_in_stock
        self.object.save()
        return response

class ProductDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete a product.
    """
    model = Product
    template_name = 'inventory/confirm_product_delete.html'
    success_url = reverse_lazy('product-list')

class PriceHistoryView(AdminRequiredMixin, ListView):
    """
    Display the price history for a specific product.
    """
    model = PriceHistory
    template_name = 'inventory/price_history.html'
    context_object_name = 'price_history'

    def get_queryset(self):
        return PriceHistory.objects.filter(product_id=self.kwargs['pk'])