from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'address')
    search_fields = ('telegram_id', 'description', 'address')
    list_filter = ('treatment_preferences',)