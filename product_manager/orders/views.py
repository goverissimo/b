from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy
from django.db import transaction
from .models import Order
from .forms import OrderForm, OrderItemFormSet
from bot_manager import notify_management_bot

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class OrderListView(AdminRequiredMixin, ListView):
    """
    Display a list of orders.
    """
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    paginate_by = 20

class OrderDetailView(AdminRequiredMixin, DetailView):
    """
    Display details of a specific order.
    """
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

class OrderUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update an existing order.
    """
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('order-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            context['items_formset'] = OrderItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        if form.is_valid() and items_formset.is_valid():
            self.object = form.save()
            items_formset.instance = self.object
            items_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class OrderCreateView(AdminRequiredMixin, CreateView):
    """
    Create a new order.
    """
    model = Order
    form_class = OrderForm
    template_name = 'orders/create_order.html'
    success_url = reverse_lazy('orders:order-list')

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        if form.is_valid() and items_formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save(commit=False)
                    self.object.created_by = self.request.user
                    self.object.status = 'pending'
                    self.object.telegram_user_id = self.request.user.id
                    self.object.save()
                    
                    items_formset.instance = self.object
                    items_formset.save()

                messages.success(self.request, 'Order created successfully.')
                return super().form_valid(form)
            except Exception as e:
                messages.error(self.request, str(e))
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items_formset'] = OrderItemFormSet(self.request.POST)
        else:
            data['items_formset'] = OrderItemFormSet()
        return data

    def form_invalid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        return self.render_to_response(self.get_context_data(form=form, items_formset=items_formset))

@require_POST
def change_order_status(request, pk):
    """
    Change the status of an order and update inventory accordingly.
    """
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('new_status')
    if new_status in dict(Order.STATUS_CHOICES):
        old_status = order.status
        order.status = new_status
        
        try:
            with transaction.atomic():
                if new_status == 'completed' and old_status != 'completed':
                    for item in order.items.all():
                        product = item.product
                        if product.quantity_in_stock >= item.quantity:
                            product.quantity_in_stock -= item.quantity
                            product.quantity_sold += item.quantity
                            product.save()
                        else:
                            raise ValueError(f"Not enough stock for product: {product.name}")
                elif new_status == 'cancelled' and old_status != 'cancelled':
                    for item in order.items.all():
                        product = item.product
                        product.quantity_in_stock += item.quantity
                        product.quantity_sold -= item.quantity
                        product.save()
                
                order.save()
                messages.success(request, f'Order status updated to {new_status}')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error updating order status: {str(e)}')
    else:
        messages.error(request, 'Invalid status')
    
    return redirect('orders:order-detail', pk=pk)

def passed_orders(request, telegram_id):
    """
    Display completed orders for a specific telegram user.
    """
    orders = Order.objects.filter(telegram_user_id=telegram_id, status='completed')
    return render(request, 'orders/passed_orders.html', {'passed_orders': orders, 'telegram_id': telegram_id})