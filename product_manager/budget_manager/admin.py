from django.contrib import admin
from .models import Expense, Income

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'date')
    list_filter = ('date',)
    search_fields = ('name', 'description')

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'date')
    list_filter = ('date',)
    search_fields = ('order__id',)