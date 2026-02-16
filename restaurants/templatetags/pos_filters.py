from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def payment_color(payment_method):
    """Return Bootstrap color class for payment method"""
    colors = {
        'cash': 'success',
        'card': 'primary',
        'mpesa': 'warning'
    }
    return colors.get(payment_method, 'secondary')
