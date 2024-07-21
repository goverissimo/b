# inventory/management/commands/sync_telegram_data.py
from django.core.management.base import BaseCommand
from inventory.models import Product
from orders.models import Order, OrderItem
import sqlite3

class Command(BaseCommand):
    help = 'Syncs data from Telegram bot SQLite database'

    def handle(self, *args, **options):
        # Connect to the Telegram bot's SQLite database
        conn = sqlite3.connect('/Users/bitcraze/Desktop/testebot/product_images/meetings.db')
        cursor = conn.cursor()

        # Sync products
        cursor.execute("SELECT id, name, price, description, images FROM products")
        for row in cursor.fetchall():
            Product.objects.update_or_create(
                id=row[0],
                defaults={
                    'name': row[1],
                    'price': row[2],
                    'description': row[3],
                    'image': row[4]
                }
            )

        # Sync orders
        cursor.execute("""
            SELECT m.id, m.user_id, m.meeting_time, m.status, 
                   SUM(oi.price * oi.quantity) as total_price
            FROM meetings m
            JOIN ordered_items oi ON m.id = oi.booking_id
            GROUP BY m.id
        """)
        for row in cursor.fetchall():
            order, created = Order.objects.update_or_create(
                telegram_order_id=row[0],
                defaults={
                    'status': row[3],
                    'created_at': row[2],
                    'total_price': row[4],
                    'profit': row[4] * 0.2  # Assuming 20% profit margin
                }
            )

            # Sync order items
            cursor.execute("""
                SELECT product_id, quantity, price
                FROM ordered_items
                WHERE booking_id = ?
            """, (row[0],))
            for item in cursor.fetchall():
                OrderItem.objects.update_or_create(
                    order=order,
                    product_id=item[0],
                    defaults={
                        'quantity': item[1],
                        'price': item[2]
                    }
                )

        conn.close()
        self.stdout.write(self.style.SUCCESS('Successfully synced Telegram bot data'))