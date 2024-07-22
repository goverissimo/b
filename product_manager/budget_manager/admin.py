from django.contrib import admin
from .models import Expense, Income, Debt

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


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'order', 'date_created', 'is_paid', 'date_paid')
    list_filter = ('is_paid', 'date_created', 'date_paid')
    search_fields = ('name', 'description', 'order__id')