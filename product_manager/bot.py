import os
import sys
import django
from django.utils import timezone

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product_manager.settings")
django.setup()

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import requests
from availability.models import AvailabilitySlot, AppointmentDuration
# Now you can import Django models and other modules
from inventory.models import Product
from orders.models import Order, OrderItem
from bot_integration.models import TelegramUser
from bot_manager import notify_management_bot as manager_notify
from bot_manager import notify_management_bot
bot = telebot.TeleBot("7311533496:AAGd2WlJQ8C9g208TpVS0Uzo0b6rQTcU4tc")

SLOTS_PER_PAGE = 8

def create_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("🛍️ View Products"))
    markup.add(KeyboardButton("📋 My Bookings"))
    markup.add(KeyboardButton("🛒 View Cart"))
    markup.add(KeyboardButton("📞 Contact Support"))
    return markup

def get_products():
    return Product.objects.filter(quantity_in_stock__gt=0).values('id', 'name', 'price', 'description', 'image')

def show_product_menu(chat_id):
    products = get_products()
    markup = InlineKeyboardMarkup()
    for product in products:
        button_text = f"{product['name']} - ${product['price']:.2f}"
        callback_data = f"view_product_{product['id']}"
        markup.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    if products:
        bot.send_message(chat_id, "Please select a product:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Sorry, there are no products available at the moment.")
        
def show_product_details(chat_id, product_id):
    try:
        product = Product.objects.get(id=product_id)
        text = f"Product: {product.name}\n"
        text += f"Price: ${product.price:.2f}\n"
        text += f"Description: {product.description}\n"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Add to Cart", callback_data=f"add_to_cart_{product_id}"))
        markup.add(InlineKeyboardButton("Back to Menu", callback_data="show_menu"))
        
        if product.image:
            with open(product.image.path, 'rb') as photo:
                bot.send_photo(chat_id, photo=photo, caption=text, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
    except Product.DoesNotExist:
        bot.send_message(chat_id, "Product not found.")

def get_available_slots(start_date, end_date):
    appointment_duration = AppointmentDuration.objects.first()
    if not appointment_duration:
        return []  # No appointment duration set

    duration_minutes = appointment_duration.duration
    
    available_slots = []
    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.strftime('%a').upper()
        availability_slots = AvailabilitySlot.objects.filter(day_of_week=day_of_week)
        
        for slot in availability_slots:
            current_time = timezone.make_aware(
                timezone.datetime.combine(current_date, slot.start_time)
            )
            end_time = timezone.make_aware(
                timezone.datetime.combine(current_date, slot.end_time)
            )
            
            while current_time + timedelta(minutes=duration_minutes) <= end_time:
                if not Order.objects.filter(meeting_time=current_time).exists():
                    available_slots.append(current_time)
                current_time += timedelta(minutes=duration_minutes)
        
        current_date += timedelta(days=1)
    
    return available_slots

def show_time_slots(chat_id, slots, page, message_id=None, product_id=None, editing_id=None, checkout=False):
    markup = InlineKeyboardMarkup()
    
    start_idx = page * SLOTS_PER_PAGE
    end_idx = start_idx + SLOTS_PER_PAGE
    
    current_date = None
    for slot in slots[start_idx:end_idx]:
        if current_date != slot.date():
            current_date = slot.date()
            markup.add(InlineKeyboardButton(text=f"--- {current_date.strftime('%Y-%m-%d')} ---", callback_data="ignore"))
        
        if checkout:
            callback_data = f"book_checkout_{slot.isoformat()}"
        elif editing_id:
            callback_data = f"editbook_{editing_id}_{slot.isoformat()}"
        elif product_id:
            callback_data = f"book_{product_id}_{slot.isoformat()}"
        else:
            callback_data = f"book_{slot.isoformat()}"
        
        markup.add(InlineKeyboardButton(text=slot.strftime("%H:%M"), callback_data=callback_data))
    
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page}_{'checkout' if checkout else product_id or 'new'}_{editing_id or 'new'}"))
    if end_idx < len(slots):
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+2}_{'checkout' if checkout else product_id or 'new'}_{editing_id or 'new'}"))
    
    if nav_row:
        markup.row(*nav_row)
    
    text = f"Select a time slot {'for your appointment ' if checkout else ''}(Page {page+1}):"
    
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)
        
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    welcome_text = ("Welcome to our booking bot!\n\n"
                    "Here's what you can do:\n"
                    "• View our products and add them to your cart\n"
                    "• Check your cart and proceed to checkout\n"
                    "• View your upcoming bookings\n"
                    "• Contact our support team if you need help\n\n"
                    "Please choose an option from the menu below:")
    bot.reply_to(message, welcome_text, reply_markup=create_main_menu())
    
@bot.message_handler(func=lambda message: message.text == "📞 Contact Support")
def contact_support(message):
    support_text = ("To contact our support team, please use one of the following methods:\n\n"
                    "1. Email: support@example.com\n"
                    "2. Phone: +1 (555) 123-4567\n"
                    "3. Live Chat: Visit our website at www.example.com\n\n"
                    "Our support hours are Monday to Friday, 9 AM to 5 PM (EST).\n"
                    "We typically respond within 24 hours during business days.")
    
    bot.reply_to(message, support_text)
    
from django.utils import timezone


@bot.message_handler(func=lambda message: message.text == "📋 My Bookings")
def my_bookings(message):
    user_id = message.from_user.id
    
    # First, try to get bookings using TelegramUser
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=user_id)
        bookings = Order.objects.filter(telegram_user_id=telegram_user.telegram_id, meeting_time__gt=timezone.now()).order_by('meeting_time')
    except TelegramUser.DoesNotExist:
        # If TelegramUser doesn't exist, try to get bookings directly using telegram_user_id
        bookings = Order.objects.filter(telegram_user_id=user_id, meeting_time__gt=timezone.now()).order_by('meeting_time')
    
    if bookings.exists():
        text = "Your upcoming bookings:\n\n"
        for booking in bookings:
            text += f"Order ID: {booking.id}\nMeeting Time: {booking.meeting_time}\n\n"
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "You have no upcoming bookings.")
@bot.message_handler(func=lambda message: message.text == "🛍️ View Products")
def view_products(message):
    show_product_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "show_menu")
def callback_show_menu(call):
    show_product_menu(call.message.chat.id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_product_'))
def callback_view_product(call):
    product_id = int(call.data.split('_')[2])
    show_product_details(call.message.chat.id, product_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('confirm_yes_', 'confirm_no_')))
def handle_confirmation(call):
    response, order_id = call.data.split('_')[1:]
    order_id = int(order_id)
    
    if response == 'yes':
        new_status = 'confirmed meet'
        message = "Thank you for confirming your appointment. We look forward to seeing you!"
    else:
        new_status = 'cancelled'
        message = "We're sorry you can't make it. Your appointment has been cancelled."
    
    # Update the order status in the database
    order = Order.objects.get(id=order_id)
    order.status = new_status
    order.save()
    
    # Send a message to the user
    bot.answer_callback_query(call.id, "Thank you for your response.")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message)
    
    # Notify the management bot
    manager_notify(order_id, new_status)

@bot.callback_query_handler(func=lambda call: call.data.startswith('book_checkout_'))
def callback_book_checkout(call):
    meeting_time = datetime.fromisoformat(call.data.split('_')[2])
    user_id = call.from_user.id
    
    # Check if the selected time is still available
    appointment_duration = AppointmentDuration.objects.first()
    if not appointment_duration:
        bot.answer_callback_query(call.id, "Appointment duration not set. Please contact support.")
        return

    day_of_week = meeting_time.strftime('%a').upper()
    availability_slot = AvailabilitySlot.objects.filter(
        day_of_week=day_of_week,
        start_time__lte=meeting_time.time(),
        end_time__gte=(meeting_time + timedelta(minutes=appointment_duration.duration)).time()
    ).first()

    if not availability_slot:
        bot.answer_callback_query(call.id, "Selected time is no longer available. Please choose another time.")
        return

    order = Order.objects.filter(telegram_user_id=user_id, status='pending_appointment').first()
    
    if order:
        # Check availability again before finalizing
        unavailable_items = []
        for item in order.items.all():
            if item.quantity > item.product.quantity_in_stock:
                unavailable_items.append(item.product.name)
        
        if unavailable_items:
            message = "Sorry, the following items are no longer available in the requested quantity:\n"
            message += "\n".join(unavailable_items)
            message += "\nYour order could not be completed. Please try again."
            bot.answer_callback_query(call.id, "Order could not be completed.")
            bot.send_message(call.message.chat.id, message)
            order.status = 'cart'  # Reset to cart status
            order.save()
            return
        
        # Update order status and meeting time
        order.status = 'pending'  # or 'pending', depending on your workflow
        order.meeting_time = meeting_time
        order.save()
        
        # Update product quantities
        for item in order.items.all():
            product = item.product
            product.quantity_in_stock -= item.quantity
            product.quantity_sold += item.quantity
            product.save()
        
        bot.answer_callback_query(call.id, "Appointment booked successfully!")
        confirmation_text = "Your appointment has been booked and your order is confirmed!\n\n"
        confirmation_text += f"Date and Time: {meeting_time.strftime('%Y-%m-%d %H:%M')}\n\n"
        confirmation_text += "Order details:\n"
        for item in order.items.all():
            confirmation_text += f"{item.product.name} x{item.quantity} - ${item.price * item.quantity:.2f}\n"
        confirmation_text += f"\nTotal: ${order.total_price:.2f}"
        
        bot.send_message(call.message.chat.id, confirmation_text)
        
        # Notify the management bot
        notify_management_bot(order.id, order.status)
    else:
        bot.answer_callback_query(call.id, "No pending order found.")
        bot.send_message(call.message.chat.id, "Sorry, we couldn't find your order. Please try checking out again.")
        
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))
def callback_add_to_cart(call):
    product_id = int(call.data.split('_')[3])
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Please enter the quantity you want to add to your cart:")
    bot.register_next_step_handler(msg, process_quantity_step, product_id)
                                   
from decimal import Decimal

from django.db import IntegrityError

# bot.py

def process_quantity_step(message, product_id):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError
        
        product = Product.objects.get(id=product_id)
        
        if quantity > product.quantity_in_stock:
            bot.reply_to(message, f"Sorry, only {product.quantity_in_stock} units are available. Please enter a smaller quantity.")
            return
        
        user_id = message.from_user.id
        
        cart_order, created = Order.objects.get_or_create(
            telegram_user_id=user_id,
            status='cart',
            defaults={
                'total_price': 0,
                'profit': 0
            }
        )

        cart_item, item_created = OrderItem.objects.get_or_create(
            order=cart_order,
            product=product,
            defaults={'quantity': 0, 'price': product.price}
        )
        
        cart_item.quantity += quantity
        cart_item.save()
        
        cart_order.total_price += Decimal(product.price) * quantity
        cart_order.save()
        
        bot.send_message(message.chat.id, f"{quantity} x {product.name} added to your cart.")
        bot.send_message(message.chat.id, "You can continue shopping or click 'Cart' to view your cart and proceed to book an appointment.", reply_markup=create_main_menu())
        
    except ValueError:
        bot.reply_to(message, "Please enter a valid positive number for quantity.")
        msg = bot.send_message(message.chat.id, "Please enter the quantity you want to add to your cart:")
        bot.register_next_step_handler(msg, process_quantity_step, product_id)
    except Product.DoesNotExist:
        bot.reply_to(message, "Sorry, this product doesn't exist.")
        
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_product_'))
def callback_buy_product(call):
    product_id = int(call.data.split('_')[2])
    bot.answer_callback_query(call.id)
    
    msg = bot.send_message(call.message.chat.id, "Please enter the quantity you want to buy:")
    bot.register_next_step_handler(msg, process_quantity_step, product_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('book_appointment_'))
def callback_book_appointment(call):
    product_id = int(call.data.split('_')[2])
    now = datetime.now()
    end = now.replace(hour=23, minute=59, second=59) + timedelta(days=7)  # Show slots for the next 7 days
    available_slots = get_available_slots(now, end)
    show_time_slots(call.message.chat.id, available_slots, 0, product_id=product_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('book_'))
def callback_book(call):
    parts = call.data.split('_')
    product_id = int(parts[1])
    meeting_time = datetime.fromisoformat(parts[2])
    user_id = call.from_user.id
    
    product = Product.objects.get(id=product_id)
    
    # Create a new order
    order = Order.objects.create(
        telegram_user_id=user_id,
        meeting_time=meeting_time,
        status='pending',
        total_price=product.price,
        profit=product.price * Decimal('0.2')  # Assuming 20% profit
    )
    
    # Add item to the order
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )
    
    bot.answer_callback_query(call.id, "Booking confirmed!")
    confirmation_text = f"Your appointment is confirmed:\n"
    confirmation_text += f"Order ID: {order.id}\n"
    confirmation_text += f"Product: {product.name}\n"
    confirmation_text += f"Price: ${product.price:.2f}\n"
    confirmation_text += f"Date and Time: {meeting_time.strftime('%Y-%m-%d %H:%M')}"
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=confirmation_text)

    # Notify the management bot
    manager_notify(order.id, 'pending')

@bot.message_handler(commands=['booking'])
def view_booking(message):
    try:
        order = Order.objects.get(id=booking_id, telegram_order_id=user_id)
        booking_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "Please provide a valid booking ID. Usage: /booking <booking_id>")
        return
    except Order.DoesNotExist:
        bot.reply_to(message, "Booking not found or you don't have permission to view it.")

    user_id = message.from_user.id
    telegram_user, _ = TelegramUser.objects.get_or_create(telegram_id=user_id)
    
    try:
        order = Order.objects.get(id=booking_id, user=telegram_user.user)
        text = f"Booking ID: {order.id}\n"
        text += f"Date and Time: {order.meeting_time.strftime('%Y-%m-%d %H:%M')}\n\n"
        text += "Order details:\n"
        total = 0
        for item in order.items.all():
            item_total = item.price * item.quantity
            total += item_total
            text += f"{item.product.name} x{item.quantity} - ${item_total:.2f}\n"
        text += f"\nTotal: ${total:.2f}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Cancel Booking", callback_data=f"cancel_{booking_id}"))
        
        bot.reply_to(message, text, reply_markup=markup)
    except Order.DoesNotExist:
        bot.reply_to(message, "Booking not found or you don't have permission to view it.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_'))
def callback_cancel_booking(call):
    booking_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    telegram_user, _ = TelegramUser.objects.get_or_create(telegram_id=user_id)
    
    try:
        order = Order.objects.get(id=booking_id, user=telegram_user.user)
        
        # Check if the booking is in the future
        if order.meeting_time > datetime.now():
            order.status = 'cancelled'
            order.save()
            
            bot.answer_callback_query(call.id, "Booking cancelled successfully!")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Your booking for {order.meeting_time.strftime('%Y-%m-%d %H:%M')} has been cancelled.")
            
            # Notify the management bot
            manager_notify(order.id, 'cancelled')
        else:
            bot.answer_callback_query(call.id, "Cannot cancel past bookings.")
    except Order.DoesNotExist:
        bot.answer_callback_query(call.id, "Booking not found or you don't have permission to cancel it.")

@bot.message_handler(func=lambda message: message.text == "🛒 View Cart")
def view_cart_command(message):
    view_cart(message)

def view_cart(message):
    user_id = message.from_user.id
    cart_items = OrderItem.objects.filter(order__telegram_user_id=user_id, order__status='cart')
    
    if cart_items:
        text = "Your Cart:\n\n"
        total = 0
        for item in cart_items:
            item_total = item.price * item.quantity
            total += item_total
            text += f"{item.product.name} x{item.quantity} - ${item_total:.2f}\n"
        text += f"\nTotal: ${total:.2f}"
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        markup.add(KeyboardButton("✅ Checkout and Book Appointment"))
        markup.add(KeyboardButton("🗑️ Clear Cart"))
        markup.add(KeyboardButton("🔙 Back to Main Menu"))
        
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Your cart is empty.", reply_markup=create_main_menu())
        
@bot.message_handler(func=lambda message: message.text == "✅ Checkout and Book Appointment")
def checkout_command(message):
    checkout(message)

@bot.message_handler(func=lambda message: message.text == "🗑️ Clear Cart")
def clear_cart_command(message):
    user_id = message.from_user.id
    Order.objects.filter(telegram_user_id=user_id, status='cart').delete()
    bot.send_message(message.chat.id, "Your cart has been cleared.", reply_markup=create_main_menu())

@bot.message_handler(func=lambda message: message.text == "🔙 Back to Main Menu")
def back_to_main_menu(message):
    bot.send_message(message.chat.id, "Returning to main menu.", reply_markup=create_main_menu())

def checkout(query_or_message):
    if isinstance(query_or_message, telebot.types.CallbackQuery):
        user_id = query_or_message.from_user.id
        chat_id = query_or_message.message.chat.id
    else:  # It's a Message object
        user_id = query_or_message.from_user.id
        chat_id = query_or_message.chat.id

    cart_order = Order.objects.filter(telegram_user_id=user_id, status='cart').first()
    
    if cart_order:
        cart_items = cart_order.items.all()
        unavailable_items = []
        
        for item in cart_items:
            if item.quantity > item.product.quantity_in_stock:
                unavailable_items.append(item.product.name)
        
        if unavailable_items:
            message = "Sorry, the following items are no longer available in the requested quantity:\n"
            message += "\n".join(unavailable_items)
            message += "\nPlease update your cart before checking out."
            bot.send_message(chat_id, message)
            return
        
        # Change the status to 'pending_appointment' instead of 'pending'
        cart_order.status = 'pending_appointment'
        cart_order.save()
        
        # Show available time slots for booking
        now = timezone.now().date()
        end = now + timedelta(days=7)
        available_slots = get_available_slots(now, end)
        show_time_slots(chat_id, available_slots, 0, checkout=True)
    else:
        bot.send_message(chat_id, "Your cart is empty. Please add products before checking out.")
        
@bot.message_handler(commands=['checkout'])
def command_checkout(message):
    checkout(telebot.types.CallbackQuery(
        id='',
        from_user=message.from_user,
        message=message,
        chat_instance='',
        data='checkout'
    ))

@bot.callback_query_handler(func=lambda call: call.data == "ignore")
def callback_ignore(call):
    bot.answer_callback_query(call.id)

bot.polling()