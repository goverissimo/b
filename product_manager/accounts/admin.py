from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from partners.models import Partner, PartnerOrder

class PartnerInline(admin.StackedInline):
    """Inline admin interface for Partner model."""
    model = Partner
    can_delete = False
    verbose_name_plural = 'Partner'

class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    inlines = (PartnerInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_partner')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'is_partner')
    fieldsets = UserAdmin.fieldsets + (
        ('Partner Status', {'fields': ('is_partner',)}),
    )
    
    def get_inline_instances(self, request, obj=None):
        """Only show Partner inline when editing an existing user."""
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Admin interface for Partner model."""
    list_display = ('user', 'profit_split_percentage', 'total_profit')
    search_fields = ('user__username', 'user__email')

@admin.register(PartnerOrder)
class PartnerOrderAdmin(admin.ModelAdmin):
    """Admin interface for PartnerOrder model."""
    list_display = ('partner', 'order', 'partner_profit')
    list_filter = ('partner',)
    search_fields = ('partner__user__username', 'order__id')