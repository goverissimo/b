from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from .models import Expense, Income
from orders.models import Order
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class BudgetOverviewView(AdminRequiredMixin, ListView):
    """
    Display an overview of the budget, including income and expenses.
    """
    template_name = 'budget_manager/budget_overview.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        completed_orders = Order.objects.filter(status='completed').order_by('-created_at')
        expenses = Expense.objects.all().order_by('-date')
        return {
            'orders': completed_orders,
            'expenses': expenses,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_income'] = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        context['total_expenses'] = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        context['balance'] = context['total_income'] - context['total_expenses']
        return context

class ExpenseCreateView(AdminRequiredMixin, CreateView):
    """
    Create a new expense.
    """
    model = Expense
    fields = ['name', 'description', 'amount', 'date']
    template_name = 'budget_manager/expense_form.html'
    success_url = reverse_lazy('budget_manager:overview')

class ExpenseUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update an existing expense.
    """
    model = Expense
    fields = ['name', 'description', 'amount', 'date']
    template_name = 'budget_manager/expense_form.html'
    success_url = reverse_lazy('budget_manager:overview')

class ExpenseDeleteView(AdminRequiredMixin,  DeleteView):
    """
    Delete an expense.
    """
    model = Expense
    success_url = reverse_lazy('budget_manager:overview')
    template_name = 'budget_manager/expense_confirm_delete.html'