from django.views.generic import TemplateView
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json
from orders.models import Order
from inventory.models import Product
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
def admin_check(user):
    return user.is_staff or user.is_superuser

class DashboardView(AdminRequiredMixin, TemplateView):
    """
    View for displaying the analytics dashboard.
    """
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate total revenue and profit
        context['total_revenue'] = self.get_total_revenue()
        context['total_profit'] = self.get_total_profit()
        
        # Get top selling products
        context['top_products'] = self.get_top_products()
        
        # Get daily profits for the last 30 days
        context['daily_profits_json'] = self.get_daily_profits_json()
        
        return context
    
    def get_total_revenue(self):
        """Calculate total revenue from all orders."""
        return Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    def get_total_profit(self):
        """Calculate total profit from all orders."""
        return Order.objects.aggregate(total=Sum('profit'))['total'] or 0
    
    def get_top_products(self, limit=5):
        """Get top selling products."""
        return Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:limit]
    
    def get_daily_profits_json(self):
        """Get daily profits for the last 30 days in JSON format."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_profits = Order.objects.filter(created_at__gte=thirty_days_ago).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            daily_profit=Sum('profit')
        ).order_by('date')
        
        daily_profits_list = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'daily_profit': float(item['daily_profit'] or 0)
            }
            for item in daily_profits
        ]
        
        return json.dumps(daily_profits_list)