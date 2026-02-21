"""
Africa's Talking SMS Service for Mobile Meals Center
Handles sending SMS notifications for orders and rider assignments
"""

import os
import logging
from africastalking.SMS import SMSService
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

class AfricaTalkingSMS:
    """Africa's Talking SMS Service"""
    
    def __init__(self):
        """Initialize SMS service with credentials"""
        self.username = getattr(settings, 'AFRICASTALKING_USERNAME', '')
        self.api_key = getattr(settings, 'AFRICASTALKING_API_KEY', '')
        self.sender_id = getattr(settings, 'AFRICASTALKING_SENDER_ID', 'MobileMeals')
        
        # Initialize Africa's Talking
        try:
            self.sms_service = SMSService(self.username, self.api_key)
            self.is_active = True
            logger.info("Africa's Talking SMS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking SMS: {e}")
            self.sms_service = None
            self.is_active = False
    
    def send_sms(self, phone_numbers, message, sender_id=None):
        """
        Send SMS to one or multiple phone numbers
        
        Args:
            phone_numbers: str or list - Phone number(s) in international format (+254...)
            message: str - SMS message content
            sender_id: str - Custom sender ID (optional)
            
        Returns:
            dict: Response from Africa's Talking API
        """
        if not self.is_active or not self.sms_service:
            logger.error("SMS service is not active")
            return {'status': 'error', 'message': 'SMS service not available'}
        
        try:
            # Ensure phone_numbers is a list
            if isinstance(phone_numbers, str):
                phone_numbers = [phone_numbers]
            
            # Validate phone numbers (basic validation)
            valid_numbers = []
            for number in phone_numbers:
                # Remove any non-digit characters except +
                clean_number = ''.join(c for c in number if c.isdigit() or c == '+')
                # Ensure it starts with + and has proper length
                if clean_number.startswith('+') and len(clean_number) >= 12:
                    valid_numbers.append(clean_number)
                else:
                    logger.warning(f"Invalid phone number format: {number}")
            
            if not valid_numbers:
                logger.error("No valid phone numbers provided")
                return {'status': 'error', 'message': 'No valid phone numbers'}
            
            # Use custom sender ID if provided, otherwise use default
            sender = sender_id or self.sender_id
            
            # Send SMS
            response = self.sms_service.send(
                message=message,
                recipients=valid_numbers,
                sender_id=sender
            )
            
            logger.info(f"SMS sent successfully to {len(valid_numbers)} numbers")
            return {
                'status': 'success',
                'message': f"SMS sent to {len(valid_numbers)} recipients",
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {
                'status': 'error',
                'message': f"Failed to send SMS: {str(e)}"
            }
    
    def send_order_confirmation(self, order):
        """
        Send order confirmation SMS to customer
        
        Args:
            order: Order object
        """
        try:
            customer_phone = getattr(order.customer, 'phone', '')
            if not customer_phone:
                logger.warning(f"No phone number for customer {order.customer.username}")
                return
            
            message = f"""Dear {order.customer.get_full_name() or order.customer.username},

Your order #{order.order_number} has been confirmed!

Order Details:
• Restaurant: {order.restaurant.name}
• Amount: KES {order.total_amount}
• Delivery Address: {order.delivery_address}

We'll notify you when a rider is assigned.

Thank you for choosing Mobile Meals Center!
📱 +254712345678"""
            
            response = self.send_sms(customer_phone, message)
            
            if response['status'] == 'success':
                logger.info(f"Order confirmation SMS sent to {customer_phone}")
            else:
                logger.error(f"Failed to send order confirmation: {response['message']}")
                
        except Exception as e:
            logger.error(f"Error sending order confirmation: {e}")
    
    def send_rider_assignment_notification(self, delivery_assignment):
        """
        Send SMS notification to rider about new assignment
        
        Args:
            delivery_assignment: DeliveryAssignment object
        """
        try:
            rider_phone = getattr(delivery_assignment.rider.user, 'phone', '')
            if not rider_phone:
                logger.warning(f"No phone number for rider {delivery_assignment.rider.user.username}")
                return
            
            order = delivery_assignment.order
            message = f"""Hello {delivery_assignment.rider.user.get_full_name() or delivery_assignment.rider.user.username},

New delivery assignment!

Order Details:
• Order #: {order.order_number}
• Restaurant: {order.restaurant.name}
• Customer: {order.customer.get_full_name() or order.customer.username}
• Delivery Address: {order.delivery_address}
• Customer Phone: {order.phone}
• Delivery Fee: KES {delivery_assignment.delivery_fee}

Please accept and proceed to pickup.

Thank you!
Mobile Meals Center"""
            
            response = self.send_sms(rider_phone, message)
            
            if response['status'] == 'success':
                logger.info(f"Rider assignment SMS sent to {rider_phone}")
            else:
                logger.error(f"Failed to send rider assignment: {response['message']}")
                
        except Exception as e:
            logger.error(f"Error sending rider assignment notification: {e}")
    
    def send_customer_rider_assigned(self, delivery_assignment):
        """
        Send SMS to customer when rider is assigned
        
        Args:
            delivery_assignment: DeliveryAssignment object
        """
        try:
            customer_phone = getattr(delivery_assignment.order.customer, 'phone', '')
            if not customer_phone:
                logger.warning(f"No phone number for customer {delivery_assignment.order.customer.username}")
                return
            
            rider = delivery_assignment.rider
            order = delivery_assignment.order
            
            message = f"""Dear {order.customer.get_full_name() or order.customer.username},

Great news! A rider has been assigned to your order #{order.order_number}.

Rider Details:
• Name: {rider.user.get_full_name() or rider.user.username}
• Vehicle: {rider.get_vehicle_type_display()}
• Phone: {getattr(rider.user, 'phone', 'Not available')}

Your order is now being prepared and will be delivered soon.

Track your order status in the app!

Thank you for choosing Mobile Meals Center!
📱 +254712345678"""
            
            response = self.send_sms(customer_phone, message)
            
            if response['status'] == 'success':
                logger.info(f"Customer rider assignment SMS sent to {customer_phone}")
            else:
                logger.error(f"Failed to send customer rider assignment: {response['message']}")
                
        except Exception as e:
            logger.error(f"Error sending customer rider assignment notification: {e}")
    
    def send_order_delivered_notification(self, delivery_assignment):
        """
        Send SMS to customer when order is delivered
        
        Args:
            delivery_assignment: DeliveryAssignment object
        """
        try:
            customer_phone = getattr(delivery_assignment.order.customer, 'phone', '')
            if not customer_phone:
                logger.warning(f"No phone number for customer {delivery_assignment.order.customer.username}")
                return
            
            order = delivery_assignment.order
            message = f"""Dear {order.customer.get_full_name() or order.customer.username},

Your order #{order.order_number} has been delivered! 🎉

We hope you enjoy your meal from {order.restaurant.name}.

Please rate your delivery experience in the app.

Thank you for choosing Mobile Meals Center!
We look forward to serving you again soon.
📱 +254712345678"""
            
            response = self.send_sms(customer_phone, message)
            
            if response['status'] == 'success':
                logger.info(f"Order delivered SMS sent to {customer_phone}")
            else:
                logger.error(f"Failed to send order delivered notification: {response['message']}")
                
        except Exception as e:
            logger.error(f"Error sending order delivered notification: {e}")

# Global SMS service instance
sms_service = AfricaTalkingSMS()
