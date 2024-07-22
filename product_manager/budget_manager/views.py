from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from .models import Expense, Income, Debt
from orders.models import Order
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class BudgetOverviewView(AdminRequiredMixin, ListView):
    template_name = 'budget_manager/budget_overview.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        completed_orders = Order.objects.filter(status='completed').order_by('-created_at')
        expenses = Expense.objects.all().order_by('-date')
        paid_debts = Debt.objects.filter(is_paid=True).order_by('-date_paid')
        return {
            'orders': completed_orders,
            'expenses': expenses,
            'paid_debts': paid_debts,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate total income from completed orders
        order_income = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Calculate total income from paid debts
        debt_income = Debt.objects.filter(is_paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Total income
        total_income = order_income + debt_income
        
        # Total expenses
        total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Total debts (money owed)
        total_debts = Debt.objects.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Current balance
        balance = total_income - total_expenses
        
        context['total_income'] = total_income
        context['total_expenses'] = total_expenses
        context['total_debts'] = total_debts
        context['balance'] = balance
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


class DebtListView(AdminRequiredMixin, ListView):
    model = Debt
    template_name = 'budget_manager/debt_list.html'
    context_object_name = 'debts'

class DebtCreateView(AdminRequiredMixin, CreateView):
    model = Debt
    fields = ['name', 'description', 'amount', 'order']
    template_name = 'budget_manager/debt_form.html'
    success_url = reverse_lazy('budget_manager:debt_list')

    def form_valid(self, form):
        with transaction.atomic():
            debt = form.save()
            # Create an expense for the debt
            expense = Expense.objects.create(
                name=f"Debt: {debt.name}",
                description=debt.description,
                amount=debt.amount,
                date=debt.date_created
            )
            debt.expense = expense
            debt.save()
        messages.success(self.request, f"Debt '{debt.name}' created and expense recorded.")
        return super().form_valid(form)
class DebtUpdateView(AdminRequiredMixin, UpdateView):
    model = Debt
    fields = ['name', 'description', 'amount', 'order', 'is_paid']
    template_name = 'budget_manager/debt_form.html'
    success_url = reverse_lazy('budget_manager:debt_list')

    def form_valid(self, form):
        with transaction.atomic():
            debt = form.save()
            if debt.expense:
                debt.expense.name = f"Debt: {debt.name}"
                debt.expense.description = debt.description
                debt.expense.amount = debt.amount
                debt.expense.save()
            if debt.is_paid and not debt.income:
                income = Income.objects.create(
                    order=debt.order,
                    amount=debt.amount,
                    date=timezone.now().date()
                )
                debt.income = income
                debt.date_paid = timezone.now().date()
                debt.save()
                messages.success(self.request, f"Debt '{debt.name}' marked as paid and income recorded.")
            elif not debt.is_paid and debt.income:
                debt.income.delete()
                debt.income = None
                debt.date_paid = None
                debt.save()
                messages.success(self.request, f"Debt '{debt.name}' marked as unpaid and income removed.")
        return super().form_valid(form)
    
class DebtDeleteView(AdminRequiredMixin, DeleteView):
    model = Debt
    success_url = reverse_lazy('budget_manager:debt_list')
    template_name = 'budget_manager/debt_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        debt = self.get_object()
        if debt.expense:
            debt.expense.delete()
        if debt.income:
            debt.income.delete()
        messages.success(request, f"Debt '{debt.name}' and associated records deleted.")
        return super().delete(request, *args, **kwargs)

def mark_debt_as_paid(request, pk):
    debt = get_object_or_404(Debt, pk=pk)
    with transaction.atomic():
        if not debt.is_paid:
            debt.is_paid = True
            debt.date_paid = timezone.now().date()
            income = Income.objects.create(
                amount=debt.amount,
                date=debt.date_paid
            )
            if debt.order:
                income.order = debt.order
                income.save()
            debt.income = income
            debt.save()
            messages.success(request, f"Debt '{debt.name}' marked as paid and income recorded.")
        else:
            messages.warning(request, f"Debt '{debt.name}' is already marked as paid.")
    return redirect('budget_manager:debt_list')