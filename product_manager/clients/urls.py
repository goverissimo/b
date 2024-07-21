from django.urls import path
from . import views
from orders.views import passed_orders
app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client-list'),
    path('create/', views.client_create, name='client-create'),
    path('<int:pk>/update/', views.client_update, name='client-update'),
    path('passed-orders/<int:telegram_id>/', passed_orders, name='passed-orders'),
]