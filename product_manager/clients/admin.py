from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'telegram_id', 'address')
    search_fields = ('nickname', 'name', 'telegram_id', 'description', 'address')
    list_filter = ('treatment_preferences',)