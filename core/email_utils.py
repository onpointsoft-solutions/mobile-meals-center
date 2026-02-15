from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order, payment):
    """
    Send order confirmation email to customer
    """
    try:
        # Calculate totals for email
        subtotal = order.total_amount
        delivery_fee = Decimal('50.00')
        tax_rate = Decimal('0.08')
        tax_amount = (subtotal + delivery_fee) * tax_rate
        total_amount = subtotal + delivery_fee + tax_amount
        
        context = {
            'order': order,
            'payment': payment,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
        }
        
        # Render email templates
        subject = f'Order Confirmation #{order.order_number} - Mobile Meals Center'
        text_content = render_to_string('emails/order_confirmation.txt', context)
        html_content = render_to_string('emails/order_confirmation.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer.email],
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Order confirmation email sent to {order.customer.email} for order {order.order_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order {order.order_number}: {str(e)}")
        return False


def send_restaurant_notification_email(order, payment):
    """
    Send new order notification to restaurant
    """
    try:
        restaurant = order.restaurant
        
        # Calculate totals for email
        subtotal = order.total_amount
        delivery_fee = Decimal('50.00')
        tax_rate = Decimal('0.08')
        tax_amount = (subtotal + delivery_fee) * tax_rate
        total_amount = subtotal + delivery_fee + tax_amount
        
        context = {
            'order': order,
            'payment': payment,
            'restaurant': restaurant,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
        }
        
        # Create notification email for restaurant
        subject = f'🔔 NEW ORDER #{order.order_number} - {restaurant.name}'
        
        # Render email templates
        text_content = render_to_string('emails/restaurant_notification.txt', context)
        html_content = render_to_string('emails/restaurant_notification.html', context)
        
        # Get restaurant email - try multiple sources
        restaurant_email = None
        
        # 1. Check if restaurant has email field
        if hasattr(restaurant, 'email') and restaurant.email:
            restaurant_email = restaurant.email
        # 2. Try to get restaurant owner's email
        elif hasattr(restaurant, 'owner') and restaurant.owner and restaurant.owner.email:
            restaurant_email = restaurant.owner.email
        # 3. Try to get user who created the restaurant
        elif hasattr(restaurant, 'user') and restaurant.user and restaurant.user.email:
            restaurant_email = restaurant.user.email
        
        if restaurant_email:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[restaurant_email],
            )
            
            # Attach HTML version
            email.attach_alternative(html_content, "text/html")
            
            email.send()
            logger.info(f"Restaurant notification email sent to {restaurant_email} for order {order.order_number}")
        else:
            logger.warning(f"No email found for restaurant {restaurant.name} - order {order.order_number}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send restaurant notification email for order {order.order_number}: {str(e)}")
        return False


def send_order_status_update_email(order, new_status):
    """
    Send order status update email to customer
    """
    try:
        status_messages = {
            'confirmed': 'Your order has been confirmed and is being prepared.',
            'preparing': 'Your order is being prepared by the restaurant.',
            'ready': 'Your order is ready and will be picked up for delivery soon.',
            'out_for_delivery': 'Your order is out for delivery! The driver will contact you shortly.',
            'delivered': 'Your order has been delivered. Enjoy your meal!',
            'cancelled': 'Your order has been cancelled. If you have any questions, please contact support.',
        }
        
        context = {
            'order': order,
            'status_message': status_messages.get(new_status, f'Your order status has been updated to {new_status}.'),
        }
        
        subject = f'Order Update #{order.order_number} - {new_status.title()}'
        
        message = f"""
Hi {order.customer.first_name}!

Order Update: #{order.order_number}

{status_messages.get(new_status, f'Your order status has been updated to {new_status}.')}

Track your order: https://mobilemealscenter.co.ke/orders/{order.id}/

---
Mobile Meals Center
📧 mobilemealscenter@gmail.com | 📞 +254 702502952
"""
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer.email],
        )
        
        email.send()
        logger.info(f"Order status update email sent to {order.customer.email} for order {order.order_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order status update email for order {order.order_number}: {str(e)}")
        return False
