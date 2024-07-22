from django.urls import path
from . import views

app_name = 'budget_manager'

urlpatterns = [
    path('', views.BudgetOverviewView.as_view(), name='overview'),
    path('expense/add/', views.ExpenseCreateView.as_view(), name='add_expense'),
    path('expense/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='edit_expense'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='delete_expense'),
]