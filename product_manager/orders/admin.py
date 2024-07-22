from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Inline admin interface for OrderItem model.
    Allows editing OrderItems directly in the Order admin page.
    """
    model = OrderItem
    extra = 0  # No extra empty forms

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for Order model.
    """
    list_display = ('id', 'telegram_user_id', 'status', 'created_at', 'total_price', 'profit')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'telegram_user_id')
    inlines = [OrderItemInline]  # Include OrderItems inline

# Register OrderItem model separately
admin.site.register(OrderItem)