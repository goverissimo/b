# analytics/views.py
from django.views.generic import TemplateView
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncDate
from orders.models import Order
from inventory.models import Product
from django.utils import timezone
from datetime import timedelta
import json

class DashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Total revenue and profit
        context['total_revenue'] = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
        context['total_profit'] = Order.objects.aggregate(total=Sum('profit'))['total'] or 0
        
        # Top selling products
        context['top_products'] = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:5]
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_profits = Order.objects.filter(created_at__gte=thirty_days_ago).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            daily_profit=Sum('profit')
        ).order_by('date')
        
        # Convert daily_profits to a list of dictionaries with serializable date
        daily_profits_list = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'daily_profit': float(item['daily_profit']) if item['daily_profit'] else 0
            }
            for item in daily_profits
        ]
        
        context['daily_profits_json'] = json.dumps(daily_profits_list)
        
        return context
    
    

