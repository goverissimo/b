from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product, PriceHistory
from .forms import ProductForm
from django.core.paginator import Paginator
from django.db.models import Q


class ProductListView(ListView):
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

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product-list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.quantity_sold = self.object.quantity_bought - self.object.quantity_in_stock
        self.object.save()
        return response

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'inventory/confirm_product_delete.html'
    success_url = reverse_lazy('product-list')

class PriceHistoryView(ListView):
    model = PriceHistory
    template_name = 'inventory/price_history.html'
    context_object_name = 'price_history'

    def get_queryset(self):
        return PriceHistory.objects.filter(product_id=self.kwargs['pk'])
    

