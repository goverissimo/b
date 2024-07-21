from django.views.generic import ListView, DetailView
from .models import Order
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import reverse
from bot_manager import notify_management_bot
from .forms import OrderForm, OrderItemFormSet
from django.views.generic import CreateView 

from decimal import Decimal
class OrderListView(ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    paginate_by = 20

class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    

@require_POST
def change_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        notify_management_bot(order.id, new_status)
        messages.success(request, f'Order status updated to {new_status}.')
    else:
        messages.error(request, 'Invalid status.')
    return redirect(reverse('order-detail', kwargs={'pk': pk}))

def passed_orders(request, telegram_id):
    passed_orders = Order.objects.filter(
        telegram_user_id=telegram_id,
        status__in=['completed', 'cancelled']
    ).order_by('-created_at')
    
    context = {
        'passed_orders': passed_orders,
        'telegram_id': telegram_id,
    }
    return render(request, 'orders/passed_orders.html', context)


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/create_order.html'

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
        if items_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.total_price = Decimal('0.00')
            self.object.profit = Decimal('0.00')
            self.object.save()

            items_formset.instance = self.object
            items_formset.save()

            # Recalculate total price and profit
            total_price = Decimal('0.00')
            for item in self.object.items.all():
                total_price += item.price * item.quantity
            self.object.total_price = total_price
            self.object.profit = self.object.calculate_profit()
            self.object.save()

            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('order-detail', kwargs={'pk': self.object.pk})