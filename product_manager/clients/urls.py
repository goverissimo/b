from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client-list'),
    path('create/', views.client_create, name='client-create'),
    path('<int:pk>/update/', views.client_update, name='client-update'),
    path('<int:pk>/delete/', views.client_delete, name='client-delete'),
    path('passed-orders/<int:client_id>/', views.passed_orders, name='passed-orders'),
]