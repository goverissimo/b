from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import inlineformset_factory
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .models import Partner, PartnerOrder
from orders.models import Order, OrderItem
from orders.forms import OrderForm, OrderItemFormSet
from django.contrib.auth import get_user_model

User = get_user_model()

# Helper function to check if a user is a partner
def is_partner(user):
    return user.is_partner

@login_required
def partner_dashboard(request):
    """
    Display the appropriate dashboard based on user role.
    """
    if request.user.is_superuser:
        # Admin dashboard
        partners = Partner.objects.all()
        return render(request, 'partners/admin_dashboard.html', {'partners': partners})
    elif request.user.is_partner:
        # Partner dashboard
        partner = get_object_or_404(Partner, user=request.user)
        return render(request, 'partners/partner_dashboard.html', {'partner': partner})
    else:
        # Debug information for non-partners
        user = User.objects.get(username=request.user.username)
        partner_exists = Partner.objects.filter(user=user).exists()
        return HttpResponse(f"You are not a partner or superuser. Debug info: is_partner={user.is_partner}, partner_exists={partner_exists}")

@staff_member_required
def profit_split(request, partner_id):
    """
    Allow admin to set profit split percentage for a partner.
    """
    partner = get_object_or_404(Partner, id=partner_id)
    if request.method == 'POST':
        percentage = request.POST.get('percentage')
        partner.profit_split_percentage = percentage
        partner.save()
    return redirect('partners:dashboard')

@login_required
@user_passes_test(lambda u: u.is_partner)
def create_order(request):
    """
    Create a new order for a partner.
    """
    partner = get_object_or_404(Partner, user=request.user)
    OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemFormSet, extra=1, can_delete=True)

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, request.FILES)

        if order_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Save order
                    order = order_form.save(commit=False)
                    order.created_by = request.user
                    order.save()

                    # Save order items
                    formset.instance = order
                    formset.save()

                    # Create or get PartnerOrder
                    partner_order, created = PartnerOrder.objects.get_or_create(
                        partner=partner,
                        order=order
                    )
                    partner_order.update_profit()

                    messages.success(request, 'Order created successfully!')
                    return redirect('partners:dashboard')
            except IntegrityError as e:
                messages.error(request, f'An error occurred while creating the order: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        order_form = OrderForm(initial={'status': 'pending'})
        formset = OrderItemFormSet()

    return render(request, 'partners/create_order.html', {
        'order_form': order_form,
        'formset': formset,
        'partner': partner,
    })

@login_required
@user_passes_test(lambda u: u.is_partner)
def change_order_status(request, order_id):
    """
    Change the status of an order and update related data.
    """
    partner_order = get_object_or_404(PartnerOrder, order_id=order_id, partner__user=request.user)
    order = partner_order.order

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            
            partner_order.update_profit()
            
            # Restore stock if order is cancelled
            if new_status == 'cancelled' and old_status != 'cancelled':
                for item in order.items.all():
                    product = item.product
                    product.quantity_in_stock += item.quantity
                    product.quantity_sold -= item.quantity
                    product.save()
            
            return JsonResponse({
                'status': 'success', 
                'new_status': new_status, 
                'order_profit': str(order.profit),
                'partner_profit': str(partner_order.partner_profit)
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid status.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)