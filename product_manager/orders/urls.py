# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/change-status/', views.change_order_status, name='change-order-status'),
    path('create/', views.OrderCreateView.as_view(), name='order-create'),
    path('passed-orders/<int:client_id>/', views.passed_orders, name='passed-orders'),
]