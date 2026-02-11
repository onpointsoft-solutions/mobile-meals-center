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
import stripe
import json
import logging

from .models import Payment
from orders.models import Order
from core.email_utils import send_order_confirmation_email, send_restaurant_notification_email

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


class CreatePaymentIntentView(LoginRequiredMixin, View):
    """Create a Stripe Payment Intent for the order"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            payment_method_type = data.get('payment_method_type', 'card')
            
            order = get_object_or_404(Order, id=order_id, customer=request.user)
            
            # Calculate total amount including tax and delivery fee
            subtotal = order.total_amount
            delivery_fee = Decimal('3.99')
            tax_rate = Decimal('0.08')
            total_amount = (subtotal + delivery_fee) * (1 + tax_rate)
            
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
            
            # Handle cash on delivery - requires 60% deposit
            if payment_method_type == 'cash_on_delivery':
                # Calculate 60% deposit for cash on delivery
                deposit_percentage = Decimal('0.60')
                deposit_amount = total_amount * deposit_percentage
                
                # Create Stripe Payment Intent for 60% deposit
                intent = stripe.PaymentIntent.create(
                    amount=int(deposit_amount * 100),  # Amount in cents
                    currency='kes',
                    payment_method_types=['card', 'mpesa'],
                    metadata={
                        'order_id': str(order.id),
                        'payment_id': str(payment.id),
                        'customer_id': str(request.user.id),
                        'payment_type': 'cash_on_delivery_deposit',
                        'deposit_percentage': '60',
                        'remaining_amount': str(total_amount - deposit_amount)
                    }
                )
                
                # Update payment with deposit info
                payment.status = 'pending'
                payment.payment_method = 'cash_on_delivery'
                payment.amount = total_amount
                payment.stripe_payment_intent_id = intent.id
                payment.save()
                
                return JsonResponse({
                    'client_secret': intent.client_secret,
                    'payment_id': str(payment.id),
                    'deposit_amount': float(deposit_amount),
                    'remaining_amount': float(total_amount - deposit_amount),
                    'message': 'Pay 60% deposit now, remaining 40% on delivery'
                })
            
            # For card and M-Pesa payments, create Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Amount in cents
                currency='kes',  # Kenya Shillings
                payment_method_types=['card', 'mpesa'],  # Enable both card and M-Pesa
                metadata={
                    'order_id': str(order.id),
                    'payment_id': str(payment.id),
                    'customer_id': str(request.user.id),
                }
            )
            
            # Update payment with Stripe intent ID
            payment.stripe_payment_intent_id = intent.id
            payment.save()
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'payment_id': str(payment.id)
            })
            
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
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
        delivery_fee = Decimal('3.99')
        tax_rate = Decimal('0.08')
        tax_amount = (subtotal + delivery_fee) * tax_rate
        total_amount = subtotal + delivery_fee + tax_amount
        
        context.update({
            'order': order,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
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


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """Handle Stripe webhooks"""
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            logger.error("Invalid payload")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_payment_success(payment_intent)
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failure(payment_intent)
            
        else:
            logger.info(f"Unhandled event type: {event['type']}")
        
        return HttpResponse(status=200)
    
    def _handle_payment_success(self, payment_intent):
        """Handle successful payment"""
        try:
            payment_id = payment_intent['metadata'].get('payment_id')
            payment = Payment.objects.get(id=payment_id)
            
            payment.status = 'succeeded'
            payment.stripe_charge_id = payment_intent.get('latest_charge')
            payment.paid_at = timezone.now()
            payment.save()
            
            # Update order status
            order = payment.order
            order.status = 'confirmed'
            order.save()
            
            # Send confirmation emails
            try:
                send_order_confirmation_email(order, payment)
                send_restaurant_notification_email(order, payment)
            except Exception as e:
                logger.error(f"Failed to send emails for order {order.id}: {str(e)}")
            
            logger.info(f"Payment {payment.id} succeeded")
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for intent {payment_intent['id']}")
    
    def _handle_payment_failure(self, payment_intent):
        """Handle failed payment"""
        try:
            payment_id = payment_intent['metadata'].get('payment_id')
            payment = Payment.objects.get(id=payment_id)
            
            payment.status = 'failed'
            payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
            payment.save()
            
            logger.info(f"Payment {payment.id} failed")
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for intent {payment_intent['id']}")
