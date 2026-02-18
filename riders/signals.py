from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from .models import RiderProfile, DeliveryAssignment
from orders.models import Order


@receiver(post_save, sender=User)
def create_rider_profile(sender, instance, created, **kwargs):
    """Create rider profile when user is created with rider type"""
    if created and hasattr(instance, 'user_type') and instance.user_type == 'rider':
        # Check if rider profile already exists
        if not hasattr(instance, 'rider_profile'):
            RiderProfile.objects.create(user=instance)
            
            # Send notification to admin about new rider registration
            send_admin_notification(
                subject='New Rider Registration',
                message=f'A new rider has registered: {instance.get_full_name() or instance.username}',
                template='riders/emails/new_rider_notification.html',
                context={'user': instance}
            )


@receiver(pre_save, sender=RiderProfile)
def update_user_approval_status(sender, instance, **kwargs):
    """Update user approval status when rider profile is updated"""
    if hasattr(instance, 'user'):
        user = instance.user
        old_status = getattr(user, 'approval_status', 'pending')
        new_status = 'pending'  # Default status
        
        # Check if user has approval_status field
        if hasattr(user, 'approval_status'):
            # This would be set by admin approval
            pass
        else:
            # Set default status
            user.approval_status = new_status
            user.is_approved = False
            user.save(update_fields=['approval_status', 'is_approved'])


@receiver(post_save, sender=DeliveryAssignment)
def handle_delivery_assignment_created(sender, instance, created, **kwargs):
    """Handle actions when delivery assignment is created"""
    if created:
        # Update order status to delivering
        order = instance.order
        if order.status == 'ready':
            order.status = 'delivering'
            order.save(update_fields=['status'])
            
            # Send notification to rider
            try:
                send_rider_notification(
                    rider=instance.rider,
                    subject='New Delivery Assignment',
                    message=f'You have been assigned Order #{instance.order.id}',
                    template='riders/emails/new_assignment_notification.html',
                    context={'assignment': instance, 'order': order}
                )
            except Exception as e:
                print(f"Error sending rider notification: {e}")


@receiver(post_save, sender=DeliveryAssignment)
def handle_delivery_status_change(sender, instance, **kwargs):
    """Handle actions when delivery status changes"""
    if instance.status == 'delivered':
        # Update order status
        order = instance.order
        order.status = 'delivered'
        order.save(update_fields=['status'])
        
        # Send notification to customer
        try:
            send_customer_delivery_notification(
                order=order,
                rider=instance.rider,
                template='riders emails/order_delivered_notification.html'
            )
        except Exception as e:
            print(f"Error sending customer notification: {e}")


@receiver(post_save, sender=Order)
def handle_order_ready_for_delivery(sender, instance, created, **kwargs):
    """Handle when order is marked as ready for delivery"""
    if not created and instance.status == 'ready':
        # Check if order has existing assignment
        if not hasattr(instance, 'delivery_assignments') or not instance.delivery_assignments.exists():
            # Order is ready but not assigned, notify available riders
            notify_available_riders(instance)


def send_admin_notification(subject, message, template=None, context=None):
    """Send notification to admin about rider activities"""
    try:
        if template:
            html_message = render_to_string(template, context)
        else:
            html_message = message
        
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False
        )
    except Exception as e:
        print(f"Error sending admin notification: {e}")


def send_rider_notification(rider, subject, message, template=None, context=None):
    """Send notification to rider"""
    try:
        if template:
            html_message = render_to_string(template, context)
        else:
            html_message = message
        
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[rider.user.email],
            fail_silently=False
        )
    except Exception as e:
        print(f"Error sending rider notification: {e}")


def send_customer_delivery_notification(order, rider, template=None):
    """Send notification to customer about delivery"""
    try:
        if template:
            html_message = render_to_string(template, {'order': order, 'rider': rider})
        else:
            html_message = f"Your order #{order.id} has been delivered by {rider.user.get_full_name()}."
        
        send_mail(
            subject=f'Order #{order.id} Delivered',
            message=f'Your order #{order.id} has been successfully delivered.',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            fail_silently=False
        )
    except Exception as e:
        print(f"Error sending customer notification: {e}")


def notify_available_riders(order):
    """Notify available riders about new order"""
    try:
        # Get all approved and online riders
        available_riders = RiderProfile.objects.filter(
            is_approved=True,
            is_online=True,
            is_active=True
        )
        
        for rider in available_riders:
            send_rider_notification(
                rider=rider,
                subject=f'New Order Available: #{order.id}',
                message=f'A new order is ready for pickup: {order.restaurant.name}',
                template='riders/emails/available_order_notification.html',
                context={'order': order}
            )
    except Exception as e:
        print(f"Error notifying available riders: {e}")
