# orders/templatetags/order_extras.py


from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)