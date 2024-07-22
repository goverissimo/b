from django.contrib import admin
from .models import Partner, PartnerOrder
from accounts.models import CustomUser

class PartnerInline(admin.StackedInline):
    model = Partner
    can_delete = False
    verbose_name_plural = 'Partner'



class PartnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'profit_split_percentage', 'total_profit')
    search_fields = ('user__username', 'user__email')

class PartnerOrderAdmin(admin.ModelAdmin):
    list_display = ('partner', 'order', 'partner_profit')
    list_filter = ('partner',)
    search_fields = ('partner__user__username', 'order__id')

# Only register if not already registered
if not admin.site.is_registered(Partner):
    admin.site.register(Partner, PartnerAdmin)

if not admin.site.is_registered(PartnerOrder):
    admin.site.register(PartnerOrder, PartnerOrderAdmin)