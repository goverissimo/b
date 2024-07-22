from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    path('dashboard/', views.partner_dashboard, name='dashboard'),
    path('profit-split/<int:partner_id>/', views.profit_split, name='profit_split'),
    path('create-order/', views.create_order, name='create_order'),
    path('change-order-status/<int:order_id>/', views.change_order_status, name='change_order_status'),
]