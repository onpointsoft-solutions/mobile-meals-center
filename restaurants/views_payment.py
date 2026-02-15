from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, View
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import json
import logging
import requests
import uuid

from django.db import models
from .models import Restaurant, RestaurantPaymentProfile, RestaurantPayout, RestaurantEarning
from orders.models import Order

logger = logging.getLogger(__name__)


class RestaurantPaymentProfileView(LoginRequiredMixin, UpdateView):
    """Restaurant owner can manage their payment details"""
    model = RestaurantPaymentProfile
    template_name = 'restaurants/payment_profile.html'
    fields = ['payout_method', 'bank_name', 'bank_code', 'account_number', 'account_name', 'account_type']
    
    def get_object(self):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        profile, created = RestaurantPaymentProfile.objects.get_or_create(
            restaurant=restaurant,
            defaults={
                'payout_method': 'bank_transfer',
                'account_type': 'individual'
            }
        )
        return profile
    
    def form_valid(self, form):
        form.instance.restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        
        # Handle M-Pesa fields from POST data
        if 'mpesa_paybill_number' in self.request.POST:
            form.instance.mpesa_paybill_number = self.request.POST.get('mpesa_paybill_number', '')
        if 'mpesa_till_number' in self.request.POST:
            form.instance.mpesa_till_number = self.request.POST.get('mpesa_till_number', '')
        if 'mpesa_account_number' in self.request.POST:
            form.instance.mpesa_account_number = self.request.POST.get('mpesa_account_number', '')
        
        messages.success(self.request, 'Payment details updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('restaurants:payment_profile')


class RestaurantPayoutListView(LoginRequiredMixin, ListView):
    """Restaurant owner can view their payout history"""
    model = RestaurantPayout
    template_name = 'restaurants/payout_list.html'
    context_object_name = 'payouts'
    paginate_by = 20
    
    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        return RestaurantPayout.objects.filter(restaurant=restaurant).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        
        # Calculate totals
        total_earnings = RestaurantEarning.objects.filter(
            restaurant=restaurant, 
            is_paid_out=False
        ).aggregate(
            total=models.Sum('restaurant_earning')
        )['total'] or Decimal('0.00')
        
        context.update({
            'restaurant': restaurant,
            'total_pending_earnings': total_earnings,
            'pending_orders_count': RestaurantEarning.objects.filter(
                restaurant=restaurant, 
                is_paid_out=False
            ).count(),
        })
        return context


class RestaurantEarningListView(LoginRequiredMixin, ListView):
    """Restaurant owner can view their earnings from orders"""
    model = RestaurantEarning
    template_name = 'restaurants/earning_list.html'
    context_object_name = 'earnings'
    paginate_by = 20
    
    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        return RestaurantEarning.objects.filter(restaurant=restaurant).order_by('-created_at')


class InitiatePayoutView(LoginRequiredMixin, TemplateView):
    """Initiate payout for delivered orders"""
    template_name = 'restaurants/initiate_payout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        
        # Get unpaid earnings from delivered orders
        unpaid_earnings = RestaurantEarning.objects.filter(
            restaurant=restaurant,
            is_paid_out=False,
            order__status='delivered'
        ).select_related('order')
        
        # Calculate totals
        total_amount = sum(earning.restaurant_earning for earning in unpaid_earnings)
        
        context.update({
            'restaurant': restaurant,
            'unpaid_earnings': unpaid_earnings,
            'total_amount': total_amount,
            'payment_profile': getattr(restaurant, 'payment_profile', None),
        })
        return context
    
    def post(self, request):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        
        # Check if payment profile exists and is verified
        try:
            payment_profile = restaurant.payment_profile
            if not payment_profile.is_verified:
                messages.error(request, 'Your payment profile must be verified before initiating payouts.')
                return redirect('restaurants:initiate_payout')
        except RestaurantPaymentProfile.DoesNotExist:
            messages.error(request, 'Please set up your payment profile first.')
            return redirect('restaurants:payment_profile')
        
        # Get unpaid earnings from delivered orders
        unpaid_earnings = RestaurantEarning.objects.filter(
            restaurant=restaurant,
            is_paid_out=False,
            order__status='delivered'
        )
        
        if not unpaid_earnings.exists():
            messages.error(request, 'No unpaid earnings from delivered orders.')
            return redirect('restaurants:initiate_payout')
        
        # Calculate total amount
        total_amount = sum(earning.restaurant_earning for earning in unpaid_earnings)
        
        if total_amount <= 0:
            messages.error(request, 'No amount available for payout.')
            return redirect('restaurants:initiate_payout')
        
        try:
            # Create payout record
            payout = RestaurantPayout.objects.create(
                restaurant=restaurant,
                amount=total_amount,
                status='pending'
            )
            
            # Associate earnings with this payout
            for earning in unpaid_earnings:
                earning.payout = payout
                earning.is_paid_out = True
                earning.paid_out_at = timezone.now()
                earning.save()
                payout.orders.add(earning.order)
            
            # Handle different payout methods
            if payment_profile.payout_method == 'paystack' and payment_profile.paystack_recipient_code:
                self._initiate_paystack_transfer(payout, payment_profile)
            elif payment_profile.payout_method in ['mpesa_paybill', 'mpesa_till']:
                # For M-Pesa payouts, mark as processing (manual processing needed)
                payout.status = 'processing'
                payout.processed_at = timezone.now()
                payout.save()
                
                if payment_profile.payout_method == 'mpesa_paybill':
                    messages.success(request, f'Payout initiated for KES {total_amount}. M-Pesa Paybill transfer will be processed within 24-48 hours.')
                else:
                    messages.success(request, f'Payout initiated for KES {total_amount}. M-Pesa Till transfer will be processed within 24-48 hours.')
            else:
                # For bank transfers, mark as processing (manual processing needed)
                payout.status = 'processing'
                payout.processed_at = timezone.now()
                payout.save()
                messages.success(request, f'Payout initiated for KES {total_amount}. Bank transfer will be processed within 24-48 hours.')
            
            return redirect('restaurants:payout_detail', pk=payout.pk)
            
        except Exception as e:
            logger.error(f"Error initiating payout: {str(e)}")
            messages.error(request, f'Error initiating payout: {str(e)}')
            return redirect('restaurants:initiate_payout')
    
    def _initiate_paystack_transfer(self, payout, payment_profile):
        """Initiate transfer via Paystack"""
        try:
            headers = {
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'source': 'balance',  # Use Paystack balance
                'amount': int(payout.amount * 100),  # Convert to cents
                'recipient': payment_profile.paystack_recipient_code,
                'reference': payout.reference,
                'reason': f'Payout for {payout.restaurant.name}'
            }
            
            response = requests.post(
                'https://api.paystack.co/transfer',
                headers=headers,
                json=payload
            )
            
            response_data = response.json()
            
            if response_data.get('status'):
                payout.transfer_code = response_data['data']['transfer_code']
                payout.paystack_transfer_id = response_data['data']['id']
                payout.status = 'processing'
                payout.processed_at = timezone.now()
                payout.save()
                
                logger.info(f"Paystack transfer initiated: {payout.reference}")
            else:
                payout.status = 'failed'
                payout.failure_reason = response_data.get('message', 'Transfer initialization failed')
                payout.save()
                
                logger.error(f"Paystack transfer failed: {payout.reference} - {payout.failure_reason}")
                
        except Exception as e:
            payout.status = 'failed'
            payout.failure_reason = str(e)
            payout.save()
            logger.error(f"Paystack transfer error: {str(e)}")
            raise


class PayoutDetailView(LoginRequiredMixin, DetailView):
    """View payout details"""
    model = RestaurantPayout
    template_name = 'restaurants/payout_detail.html'
    context_object_name = 'payout'
    
    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        return RestaurantPayout.objects.filter(restaurant=restaurant)


class VerifyPaystackRecipientView(LoginRequiredMixin, View):
    """Create/verify Paystack recipient for transfers"""
    
    def post(self, request):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        
        try:
            payment_profile, created = RestaurantPaymentProfile.objects.get_or_create(
                restaurant=restaurant,
                defaults={'payout_method': 'bank_transfer'}
            )
            
            headers = {
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'type': 'nuban',
                'name': payment_profile.account_name,
                'account_number': payment_profile.account_number,
                'bank_code': payment_profile.bank_code,
                'currency': 'KES'
            }
            
            response = requests.post(
                'https://api.paystack.co/transferrecipient',
                headers=headers,
                json=payload
            )
            
            response_data = response.json()
            
            if response_data.get('status'):
                payment_profile.paystack_recipient_code = response_data['data']['recipient_code']
                payment_profile.paystack_recipient_id = response_data['data']['id']
                payment_profile.is_verified = True
                payment_profile.verification_date = timezone.now()
                payment_profile.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Paystack recipient verified successfully!',
                    'recipient_code': response_data['data']['recipient_code']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': response_data.get('message', 'Verification failed')
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error verifying Paystack recipient: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
