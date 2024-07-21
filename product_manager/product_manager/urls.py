# product_manager/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('orders/', include('orders.urls')),
    path('analytics/', include('analytics.urls')),
    path('clients/', include('clients.urls')),
    path('availability/', include('availability.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)