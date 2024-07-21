from django.urls import path
from .views import availability_settings

app_name = 'availability'
urlpatterns = [
    # ... other url patterns ...
    path('availability-settings/', availability_settings, name='availability-settings'),
]