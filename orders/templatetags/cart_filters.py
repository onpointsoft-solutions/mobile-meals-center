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
def calculate_tax(subtotal, delivery_fee=None):
    """Calculate tax on subtotal + delivery fee using database rates."""
    try:
        from core.utils import get_tax_rate, get_delivery_fee
        
        subtotal_decimal = Decimal(str(subtotal))
        if delivery_fee is None:
            delivery_fee = get_delivery_fee()
        else:
            delivery_fee = Decimal(str(delivery_fee))
        
        total_before_tax = subtotal_decimal + delivery_fee
        tax_rate = get_tax_rate() / Decimal('100')  # Convert percentage to decimal
        return total_before_tax * tax_rate
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_total(subtotal, delivery_fee=None):
    """Calculate final total with delivery fee and tax using database rates."""
    try:
        from core.utils import get_tax_rate, get_delivery_fee
        
        subtotal_decimal = Decimal(str(subtotal))
        if delivery_fee is None:
            delivery_fee = get_delivery_fee()
        else:
            delivery_fee = Decimal(str(delivery_fee))
        
        total_before_tax = subtotal_decimal + delivery_fee
        tax_rate = get_tax_rate() / Decimal('100')  # Convert percentage to decimal
        tax = total_before_tax * tax_rate
        return total_before_tax + tax
    except (ValueError, TypeError):
        return 0
