# product_manager/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import custom_login
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', custom_login, name='login'),
    path('', include('inventory.urls'), name='home'),
    path('orders/', include('orders.urls', namespace='orders')),
    path('analytics/', include('analytics.urls')),
     path('clients/', include('clients.urls', namespace='clients')),
    path('availability/', include('availability.urls')),
    path('partners/', include('partners.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('budget/', include('budget_manager.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)