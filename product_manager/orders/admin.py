from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_user_id', 'status', 'created_at', 'total_price', 'profit')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'telegram_user_id')
    inlines = [OrderItemInline]

admin.site.register(OrderItem)