from django.contrib import admin
from .models import Product, PriceHistory

class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('date',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity_in_stock', 'quantity_sold')
    list_filter = ('quantity_in_stock',)
    search_fields = ('name', 'description')
    inlines = [PriceHistoryInline]

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'date')
    list_filter = ('product',)
    date_hierarchy = 'date'