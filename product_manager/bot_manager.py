import os
import sys
import django

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product_manager.settings")
django.setup()

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
from django.conf import settings
from orders.models import Order, OrderItem
from inventory.models import Product
from bot_integration.models import TelegramUser
from datetime import datetime

# Initialize the bot with your token
MANAGEMENT_BOT_TOKEN = "7372615466:AAEF5HXEzF9Pkwi7GoV5BinYxKvsVSxqmiM"
bot = telebot.TeleBot(MANAGEMENT_BOT_TOKEN)

# Your Telegram user ID (you'll receive notifications to this ID)
ADMIN_ID = 502716959

def create_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("📋 View Pending Orders"))
    markup.row(KeyboardButton("📊 View All Orders"))
    markup.row(KeyboardButton("🔍 View Order Details"))
    return markup

def create_manage_order_menu(order_id):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Manage Order", callback_data=f"manage_{order_id}"))
    return markup

def create_order_action_menu(order_id):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Accept", callback_data=f"accept_{order_id}"),
               InlineKeyboardButton("Dispatch", callback_data=f"dispatch_{order_id}"))
    markup.row(InlineKeyboardButton("Complete", callback_data=f"complete_{order_id}"),
               InlineKeyboardButton("Cancel", callback_data=f"cancel_{order_id}"))
    return markup

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "Welcome to the Order Management Bot. Use the menu below to manage orders.", reply_markup=create_main_menu())
    else:
        bot.reply_to(message, "Sorry, this bot is for administrative use only.")

def notify_management_bot(order_id, new_status):
    MANAGEMENT_BOT_TOKEN = settings.MANAGEMENT_BOT_TOKEN
    ADMIN_ID = settings.ADMIN_TELEGRAM_ID
    url = f"https://api.telegram.org/bot{MANAGEMENT_BOT_TOKEN}/sendMessage"
    
    try:
        order = Order.objects.get(id=order_id)
        message = f"Order Update:\n"
        message += f"Order ID: {order.id}\n"
        message += f"User Telegram ID: {order.telegram_user_id}\n"
        message += f"New Status: {new_status}\n"
        message += f"Meeting Time: {order.meeting_time}\n"
        message += f"Products: {', '.join([f'{item.product.name} x{item.quantity}' for item in order.items.all()])}"
        
        payload = {
            "chat_id": ADMIN_ID,
            "text": message
        }
        
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send notification. Status code: {response.status_code}")
    except Order.DoesNotExist:
        print(f"Error: Order {order_id} not found")
        
@bot.message_handler(commands=['help'])
def send_help(message):
    if message.from_user.id == ADMIN_ID:
        help_text = """
        Available commands:
        /pending - View pending orders
        /accept <order_id> - Accept an order
        /dispatch <order_id> - Mark an order as dispatched
        /complete <order_id> - Mark an order as completed
        /details <order_id> - View details of a specific order
        """
        bot.reply_to(message, help_text)
    else:
        bot.reply_to(message, "Sorry, this bot is for administrative use only.")

@bot.message_handler(func=lambda message: message.text == "📋 View Pending Orders")
def view_pending_orders(message):
    if message.from_user.id == ADMIN_ID:
        pending_orders = Order.objects.exclude(status__in=['completed', 'cancelled']).order_by('meeting_time')
        
        if pending_orders:
            for order in pending_orders:
                text = f"Order ID: {order.id}\nUser Telegram ID: {order.telegram_user_id}\nTime: {order.meeting_time}\nStatus: {order.status}"
                bot.send_message(message.chat.id, text, reply_markup=create_manage_order_menu(order.id))
        else:
            bot.reply_to(message, "No pending orders.")
    else:
        bot.reply_to(message, "Sorry, this command is for administrative use only.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('manage_'))
def manage_order(call):
    if call.from_user.id == ADMIN_ID:
        order_id = int(call.data.split('_')[1])
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_order_action_menu(order_id))
    else:
        bot.answer_callback_query(call.id, "Sorry, this action is for administrative use only.")

@bot.message_handler(func=lambda message: message.text == "📊 View All Orders")
def view_all_orders(message):
    if message.from_user.id == ADMIN_ID:
        all_orders = Order.objects.all().order_by('-meeting_time')[:20]
        
        if all_orders:
            for order in all_orders:
                text = f"Order ID: {order.id}\nUser Telegram ID: {order.telegram_user_id}\nTime: {order.meeting_time}\nStatus: {order.status}"
                bot.send_message(message.chat.id, text, reply_markup=create_manage_order_menu(order.id))
        else:
            bot.reply_to(message, "No orders found.")
    else:
        bot.reply_to(message, "Sorry, this command is for administrative use only.")

@bot.message_handler(func=lambda message: message.text == "🔍 View Order Details")
def prompt_order_id(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.reply_to(message, "Please enter the order ID:")
        bot.register_next_step_handler(msg, view_order_details)
    else:
        bot.reply_to(message, "Sorry, this command is for administrative use only.")

def request_confirmation(user_id, order_id, meeting_time):
    meeting_time = meeting_time.strftime('%Y-%m-%d %H:%M')
    message = f"Your appointment (Order ID: {order_id}) is ready to be confirmed:\n"
    message += f"Appointment time: {meeting_time}\n"
    message += "Can you confirm your attendance? (Yes/No)"
    
    send_message_to_client(user_id, message, order_id)

def send_message_to_client(user_id, message, order_id=None):
    MAIN_BOT_TOKEN = "7311533496:AAGd2WlJQ8C9g208TpVS0Uzo0b6rQTcU4tc"
    url = f"https://api.telegram.org/bot{MAIN_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": message
    }
    if order_id:
        keyboard = {
            "inline_keyboard": [
                [{"text": "Yes", "callback_data": f"confirm_yes_{order_id}"},
                 {"text": "No", "callback_data": f"confirm_no_{order_id}"}]
            ]
        }
        payload["reply_markup"] = json.dumps(keyboard)
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send message to user {user_id}. Response: {response.text}")

def notify_client(user_telegram_id, order_id, new_status, meeting_time):
    meeting_time_str = meeting_time.strftime('%Y-%m-%d %H:%M') if meeting_time else "Not set"
    message = f"Update on your order (ID: {order_id}):\n"
    message += f"Status: {new_status.capitalize()}\n"
    message += f"Appointment time: {meeting_time_str}\n"
    
    if new_status == 'accepted':
        message += "Your order has been accepted. We'll notify you when it's ready for dispatch."
    elif new_status == 'dispatched':
        message += "Your order has been dispatched. Please confirm your appointment."
    elif new_status == 'completed':
        message += "Your order has been completed. Thank you for your business!"
    elif new_status == 'cancelled':
        message += "Your order has been cancelled. If you have any questions, please contact us."
    elif new_status == 'confirmed':
        message += "Your appointment has been confirmed. We look forward to seeing you!"
    
    send_message_to_client(user_telegram_id, message)

def view_order_details(message):
    try:
        order_id = int(message.text)
        order = Order.objects.get(id=order_id)
        
        text = f"Order ID: {order.id}\n"
        text += f"Meeting Time: {order.meeting_time}\n"
        text += f"Status: {order.status}\n"
        text += f"Products: {', '.join([f'{item.product.name} x{item.quantity}' for item in order.items.all()])}"
        bot.reply_to(message, text, reply_markup=create_manage_order_menu(order.id))
    except (ValueError, Order.DoesNotExist):
        bot.reply_to(message, "Order not found or invalid order ID.")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('accept_', 'dispatch_', 'complete_', 'cancel_')))
def handle_order_action(call):
    if call.from_user.id == ADMIN_ID:
        action, order_id = call.data.split('_')
        order_id = int(order_id)
        
        try:
            order = Order.objects.get(id=order_id)
            new_status = action + 'ed' if action != 'cancel' else 'cancelled'
            order.status = new_status
            order.save()
            
            bot.answer_callback_query(call.id, f"Order {order_id} has been marked as {new_status}.")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            
            user_telegram_id = order.telegram_user_id
            
            if action == 'dispatch':
                request_confirmation(user_telegram_id, order_id, order.meeting_time)
            else:
                notify_client(user_telegram_id, order_id, new_status, order.meeting_time)
        except Order.DoesNotExist:
            bot.answer_callback_query(call.id, f"Order {order_id} not found.")
    else:
        bot.answer_callback_query(call.id, "Sorry, this action is for administrative use only.")
        
def notify_new_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        message = f"New Order Received!\n\n"
        message += f"Order ID: {order.id}\n"
        message += f"Meeting Time: {order.meeting_time}\n"
        message += f"Products: {', '.join([f'{item.product.name} x{item.quantity}' for item in order.items.all()])}"
        
        bot.send_message(ADMIN_ID, message, reply_markup=create_manage_order_menu(order.id))
    except Order.DoesNotExist:
        print(f"Error: Order {order_id} not found")

def check_new_orders():
    new_orders = Order.objects.filter(status='new')
    
    for order in new_orders:
        notify_new_order(order.id)
        order.status = 'pending'
        order.save()

# Start the bot
bot.polling()