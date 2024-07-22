from django.urls import path
from . import views

app_name = 'budget_manager'

urlpatterns = [
    path('', views.BudgetOverviewView.as_view(), name='overview'),
    path('expense/add/', views.ExpenseCreateView.as_view(), name='add_expense'),
    path('expense/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='edit_expense'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='delete_expense'),
    path('debts/', views.DebtListView.as_view(), name='debt_list'),
    path('debts/add/', views.DebtCreateView.as_view(), name='add_debt'),
    path('debts/<int:pk>/edit/', views.DebtUpdateView.as_view(), name='edit_debt'),
    path('debts/<int:pk>/delete/', views.DebtDeleteView.as_view(), name='delete_debt'),
    path('debts/<int:pk>/mark-paid/', views.mark_debt_as_paid, name='mark_debt_paid'),
]