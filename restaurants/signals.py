from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal

from orders.models import Order
from .models import RestaurantEarning
from core.utils import get_commission_rate


@receiver(post_save, sender=Order)
def create_restaurant_earning(sender, instance, created, **kwargs):
    """
    Create restaurant earning when an order is marked as delivered
    """
    # Only create earnings when order status changes to 'delivered'
    if instance.status == 'delivered':
        # Check if earning already exists for this order
        if not hasattr(instance, 'restaurant_earning'):
            with transaction.atomic():
                # Get commission rate from database
                commission_rate = get_commission_rate() / Decimal('100')  # Convert percentage to decimal
                
                RestaurantEarning.objects.create(
                    restaurant=instance.restaurant,
                    order=instance,
                    order_amount=instance.total_amount,
                    commission_rate=commission_rate
                )
