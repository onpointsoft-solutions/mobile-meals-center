from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import json
import logging
import requests
import uuid

from .models import Payment
from orders.models import Order
from core.email_utils import send_order_confirmation_email, send_restaurant_notification_email

logger = logging.getLogger(__name__)


class CreatePaymentIntentView(LoginRequiredMixin, View):
    """Create Paystack transaction for the order"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            payment_method_type = data.get('payment_method_type', 'paystack')
            
            order = get_object_or_404(Order, id=order_id, customer=request.user)
            
            # Calculate total amount including tax and delivery fee
            subtotal = order.total_amount
            delivery_fee = Decimal('50.00')
            tax_rate = Decimal('0.08')
            total_amount = (subtotal + delivery_fee) * (1 + tax_rate)
            
            # Convert to kobo (Paystack uses kobo for NGN, but we'll use KES cents)
            amount_in_kobo = int(total_amount * 100)
            
            # Create or get existing payment
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'user': request.user,
                    'amount': total_amount,
                    'status': 'pending',
                    'payment_method': payment_method_type
                }
            )
            
            if payment_method_type == 'cash_on_delivery':
                # Handle cash on delivery - confirm order immediately
                payment.status = 'completed'
                payment.payment_method = 'cash_on_delivery'
                payment.amount = total_amount
                payment.save()
                
                # Update order status to confirmed
                order.status = 'confirmed'
                order.save()
                
                # Send confirmation emails
                try:
                    send_order_confirmation_email(order)
                    send_restaurant_notification_email(order)
                except Exception as email_error:
                    logger.error(f"Error sending emails: {str(email_error)}")
                
                return JsonResponse({
                    'success': True,
                    'payment_id': str(payment.id),
                    'message': 'Order confirmed! Pay cash on delivery.'
                })
            
            # Handle Paystack payment
            if payment_method_type == 'paystack':
                # Generate unique reference
                reference = f'MMC-{order.id}-{uuid.uuid4().hex[:8]}'
                
                # Initialize Paystack transaction
                headers = {
                    'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'email': request.user.email,
                    'amount': amount_in_kobo,
                    'reference': reference,
                    'callback_url': settings.PAYSTACK_CALLBACK_URL,
                    'metadata': {
                        'order_id': str(order.id),
                        'payment_id': str(payment.id),
                        'customer_id': str(request.user.id),
                        'custom_fields': [
                            {
                                'display_name': 'Order ID',
                                'variable_name': 'order_id',
                                'value': str(order.id)
                            },
                            {
                                'display_name': 'Customer Name',
                                'variable_name': 'customer_name',
                                'value': request.user.get_full_name() or request.user.username
                            }
                        ]
                    }
                }
                
                # Make request to Paystack
                response = requests.post(
                    'https://api.paystack.co/transaction/initialize',
                    headers=headers,
                    json=payload
                )
                
                response_data = response.json()
                
                if response_data.get('status'):
                    # Update payment with Paystack reference
                    payment.paystack_reference = reference
                    payment.save()
                    
                    return JsonResponse({
                        'success': True,
                        'authorization_url': response_data['data']['authorization_url'],
                        'reference': reference,
                        'payment_id': str(payment.id),
                        'access_code': response_data['data'].get('access_code')
                    })
                else:
                    return JsonResponse({
                        'error': response_data.get('message', 'Payment initialization failed')
                    }, status=400)
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)


class ProcessPaymentView(LoginRequiredMixin, TemplateView):
    """Display the payment form"""
    template_name = 'payments/process_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        
        order = get_object_or_404(Order, id=order_id, customer=self.request.user)
        
        # Calculate totals
        subtotal = order.total_amount
        delivery_fee = Decimal('50.00')
        tax_rate = Decimal('0.08')
        tax_amount = (subtotal + delivery_fee) * tax_rate
        total_amount = subtotal + delivery_fee + tax_amount
        
        context.update({
            'order': order,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY
        })
        return context


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """Display payment success page"""
    template_name = 'payments/payment_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = kwargs.get('payment_id')
        
        payment = get_object_or_404(Payment, id=payment_id, user=self.request.user)
        context['payment'] = payment
        context['order'] = payment.order
        return context


class PaymentFailedView(LoginRequiredMixin, TemplateView):
    """Display payment failure page"""
    template_name = 'payments/payment_failed.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = kwargs.get('payment_id')
        
        payment = get_object_or_404(Payment, id=payment_id, user=self.request.user)
        context['payment'] = payment
        context['order'] = payment.order
        return context


class PaystackVerificationView(LoginRequiredMixin, View):
    """Handle Paystack payment verification"""
    
    def get(self, request):
        reference = request.GET.get('reference')
        
        if not reference:
            messages.error(request, 'Payment verification failed: No reference provided')
            return redirect('core:home')
        
        try:
            # Verify transaction with Paystack
            headers = {
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'https://api.paystack.co/transaction/verify/{reference}',
                headers=headers
            )
            
            response_data = response.json()
            
            if response_data.get('status') and response_data['data']['status'] == 'success':
                # Find payment by reference
                payment = Payment.objects.get(paystack_reference=reference)
                
                # Update payment status
                payment.status = 'succeeded'
                payment.paystack_transaction_id = response_data['data']['id']
                payment.paid_at = timezone.now()
                payment.save()
                
                # Update order status
                order = payment.order
                order.status = 'confirmed'
                order.save()
                
                # Send confirmation emails
                try:
                    send_order_confirmation_email(order)
                    send_restaurant_notification_email(order)
                except Exception as e:
                    logger.error(f"Failed to send emails for order {order.id}: {str(e)}")
                
                messages.success(request, 'Payment successful! Your order has been confirmed.')
                return redirect('payments:payment_success', payment_id=payment.id)
            else:
                # Payment failed
                payment = Payment.objects.get(paystack_reference=reference)
                payment.status = 'failed'
                payment.failure_reason = response_data.get('message', 'Payment verification failed')
                payment.save()
                
                messages.error(request, 'Payment failed. Please try again.')
                return redirect('payments:payment_failed', payment_id=payment.id)
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for reference {reference}")
            messages.error(request, 'Payment verification failed: Payment not found')
            return redirect('core:home')
        except Exception as e:
            logger.error(f"Error verifying Paystack payment: {str(e)}")
            messages.error(request, 'Payment verification failed. Please contact support.')
            return redirect('core:home')
