from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_tax(subtotal, delivery_fee=50.00):
    """Calculate 8% tax on subtotal + delivery fee."""
    try:
        total_before_tax = Decimal(str(subtotal)) + Decimal(str(delivery_fee))
        return total_before_tax * Decimal('0.08')
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_total(subtotal, delivery_fee=50.00):
    """Calculate final total with delivery fee and 8% tax."""
    try:
        subtotal_decimal = Decimal(str(subtotal))
        delivery_decimal = Decimal(str(delivery_fee))
        total_before_tax = subtotal_decimal + delivery_decimal
        tax = total_before_tax * Decimal('0.08')
        return total_before_tax + tax
    except (ValueError, TypeError):
        return 0
