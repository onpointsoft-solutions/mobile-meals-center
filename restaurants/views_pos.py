from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from decimal import Decimal
import json
import logging

from .models import Restaurant
from .models_pos import POSSession, POSOrder, POSOrderItem, POSReceipt
from meals.models import Meal, Category

logger = logging.getLogger(__name__)


class POSMainView(LoginRequiredMixin, TemplateView):
    """Main POS interface for restaurants"""
    template_name = 'restaurants/pos/main.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Ensure user is restaurant owner
        if not request.user.is_restaurant:
            messages.error(request, 'Access denied. Restaurant owners only.')
            return redirect('restaurants:dashboard')
        
        # Get or create active session
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        active_session = POSSession.objects.filter(
            restaurant=restaurant, 
            is_active=True
        ).first()
        
        if not active_session:
            # Create new session
            active_session = POSSession.objects.create(
                restaurant=restaurant,
                opened_by=request.user,
                opening_balance=Decimal('0.00')
            )
            messages.success(request, f'New POS session started: {active_session.id}')
        
        self.active_session = active_session
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        
        # Get meals organized by category
        categories = Category.objects.filter(meal__restaurant=restaurant).distinct()
        meals_by_category = {}
        for category in categories:
            meals_by_category[category] = restaurant.meals.filter(
                category=category, 
                is_available=True
            )
        
        # Uncategorized meals
        uncategorized = restaurant.meals.filter(category__isnull=True, is_available=True)
        if uncategorized.exists():
            meals_by_category['Uncategorized'] = uncategorized
        
        # Active orders
        active_orders = POSOrder.objects.filter(
            session=self.active_session,
            status='active'
        ).prefetch_related('items')
        
        context.update({
            'restaurant': restaurant,
            'session': self.active_session,
            'meals_by_category': meals_by_category,
            'active_orders': active_orders,
            'categories': categories,
        })
        return context


class POSCreateOrderView(LoginRequiredMixin, View):
    """Create new POS order"""
    
    def post(self, request):
        if not request.user.is_restaurant:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        active_session = POSSession.objects.filter(
            restaurant=restaurant, 
            is_active=True
        ).first()
        
        if not active_session:
            return JsonResponse({'error': 'No active POS session'}, status=400)
        
        try:
            # Create new order
            order = POSOrder.objects.create(
                session=active_session,
                restaurant=restaurant,
                total_amount=Decimal('0.00'),
                payment_method='cash',
                status='active'
            )
            
            return JsonResponse({
                'success': True,
                'order_id': str(order.id),
                'order_number': order.order_number
            })
            
        except Exception as e:
            logger.error(f"Error creating POS order: {str(e)}")
            return JsonResponse({'error': 'Failed to create order'}, status=500)


class POSAddItemView(LoginRequiredMixin, View):
    """Add item to POS order"""
    
    def post(self, request):
        if not request.user.is_restaurant:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            meal_id = data.get('meal_id')
            quantity = int(data.get('quantity', 1))
            notes = data.get('notes', '')
            
            order = get_object_or_404(POSOrder, id=order_id, status='active')
            meal = get_object_or_404(Meal, id=meal_id)
            
            # Check if meal belongs to restaurant
            if meal.restaurant != order.restaurant:
                return JsonResponse({'error': 'Invalid meal for this restaurant'}, status=400)
            
            # Add item to order
            order_item = POSOrderItem.objects.create(
                order=order,
                meal=meal,
                quantity=quantity,
                price=meal.price,
                notes=notes
            )
            
            # Update order total
            self._update_order_total(order)
            
            return JsonResponse({
                'success': True,
                'item_id': str(order_item.id),
                'item_total': float(order_item.total_price),
                'order_total': float(order.total_amount)
            })
            
        except Exception as e:
            logger.error(f"Error adding item to POS order: {str(e)}")
            return JsonResponse({'error': 'Failed to add item'}, status=500)
    
    def _update_order_total(self, order):
        """Update order total amount"""
        total = order.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or Decimal('0.00')
        order.total_amount = total
        order.save()


class POSRemoveItemView(LoginRequiredMixin, View):
    """Remove item from POS order"""
    
    def post(self, request):
        if not request.user.is_restaurant:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            
            order_item = get_object_or_404(POSOrderItem, id=item_id)
            order = order_item.order
            
            # Check if order belongs to user's restaurant
            if order.restaurant.owner != request.user:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            order_item.delete()
            
            # Update order total
            total = order.items.aggregate(
                total=Sum(F('quantity') * F('price'))
            )['total'] or Decimal('0.00')
            order.total_amount = total
            order.save()
            
            return JsonResponse({
                'success': True,
                'order_total': float(order.total_amount)
            })
            
        except Exception as e:
            logger.error(f"Error removing item from POS order: {str(e)}")
            return JsonResponse({'error': 'Failed to remove item'}, status=500)


class POSCompleteOrderView(LoginRequiredMixin, View):
    """Complete POS order with payment"""
    
    def post(self, request):
        if not request.user.is_restaurant:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            payment_method = data.get('payment_method')
            customer_name = data.get('customer_name', '')
            customer_email = data.get('customer_email', '')
            customer_phone = data.get('customer_phone', '')
            
            order = get_object_or_404(POSOrder, id=order_id, status='active')
            
            # Check if order belongs to user's restaurant
            if order.restaurant.owner != request.user:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            # Update order details
            order.payment_method = payment_method
            order.customer_name = customer_name
            order.customer_email = customer_email
            order.customer_phone = customer_phone
            order.complete_order()
            
            # Update session sales
            session = order.session
            if payment_method == 'cash':
                session.cash_sales += order.total_amount
            elif payment_method == 'card':
                session.card_sales += order.total_amount
            elif payment_method == 'mpesa':
                session.mpesa_sales += order.total_amount
            session.save()
            
            # Create receipt
            receipt = POSReceipt.objects.create(
                order=order,
                customer_name=customer_name,
                customer_email=customer_email
            )
            
            return JsonResponse({
                'success': True,
                'order_id': str(order.id),
                'order_number': order.order_number,
                'receipt_id': str(receipt.id),
                'receipt_number': receipt.receipt_number
            })
            
        except Exception as e:
            logger.error(f"Error completing POS order: {str(e)}")
            return JsonResponse({'error': 'Failed to complete order'}, status=500)


class POSReportsView(LoginRequiredMixin, TemplateView):
    """POS reporting dashboard"""
    template_name = 'restaurants/pos/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        
        # Get date range (default to today)
        from datetime import date, timedelta
        today = date.today()
        start_date = request.GET.get('start_date', today)
        end_date = request.GET.get('end_date', today)
        
        # Get orders for date range
        orders = POSOrder.objects.filter(
            restaurant=restaurant,
            created_at__date__range=[start_date, end_date],
            status='completed'
        )
        
        # Calculate metrics
        total_sales = orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        order_count = orders.count()
        avg_order_value = total_sales / order_count if order_count > 0 else Decimal('0.00')
        
        # Payment method breakdown
        payment_breakdown = orders.values('payment_method').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        # Top selling items
        top_items = POSOrderItem.objects.filter(
            order__in=orders
        ).values('meal__name').annotate(
            quantity=Sum('quantity'),
            revenue=Sum(F('quantity') * F('price'))
        ).order_by('-quantity')[:10]
        
        # Hourly sales
        hourly_sales = orders.extra({
            'hour': "strftime('%%H', created_at)"
        }).values('hour').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('hour')
        
        context.update({
            'restaurant': restaurant,
            'orders': orders,
            'total_sales': total_sales,
            'order_count': order_count,
            'avg_order_value': avg_order_value,
            'payment_breakdown': payment_breakdown,
            'top_items': top_items,
            'hourly_sales': hourly_sales,
            'start_date': start_date,
            'end_date': end_date,
        })
        return context


class POSSessionsView(LoginRequiredMixin, ListView):
    """Manage POS sessions"""
    model = POSSession
    template_name = 'restaurants/pos/sessions.html'
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        return POSSession.objects.filter(restaurant=restaurant).order_by('-opened_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        
        # Active session
        active_session = POSSession.objects.filter(
            restaurant=restaurant,
            is_active=True
        ).first()
        
        context.update({
            'restaurant': restaurant,
            'active_session': active_session,
        })
        return context


class POSCloseSessionView(LoginRequiredMixin, View):
    """Close POS session"""
    
    def post(self, request):
        if not request.user.is_restaurant:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            closing_balance = Decimal(data.get('closing_balance', '0'))
            notes = data.get('notes', '')
            
            session = get_object_or_404(POSSession, id=session_id)
            
            # Check if session belongs to user's restaurant
            if session.restaurant.owner != request.user:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            # Close session
            session.close_session(closing_balance=closing_balance)
            session.notes = notes
            session.save()
            
            return JsonResponse({
                'success': True,
                'session_id': str(session.id),
                'total_sales': float(session.total_sales),
                'order_count': session.order_count
            })
            
        except Exception as e:
            logger.error(f"Error closing POS session: {str(e)}")
            return JsonResponse({'error': 'Failed to close session'}, status=500)


class POSReceiptView(LoginRequiredMixin, DetailView):
    """View and print POS receipt"""
    model = POSReceipt
    template_name = 'restaurants/pos/receipt.html'
    context_object_name = 'receipt'
    
    def get_object(self):
        receipt = get_object_or_404(POSReceipt, pk=self.kwargs['pk'])
        
        # Check if receipt belongs to user's restaurant
        if receipt.order.restaurant.owner != self.request.user:
            messages.error(self.request, 'Access denied.')
            return None
        
        return receipt


classPOSEmailReceiptView(LoginRequiredMixin, View):
    
    def post(self, request, pk):
        receipt = get_object_or_404(POSReceipt, pk=pk)
        
        # Check if receipt belongs to user's restaurant
        if receipt.order.restaurant.owner != request.user:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        if not receipt.customer_email:
            return JsonResponse({'error': 'No customer email address provided'}, status=400)
        
        try:
            from core.email_utils import send_pos_receipt_email
            
            # Send email receipt
            send_pos_receipt_email(receipt)
            
            # Mark receipt as sent
            receipt.emailed_at = timezone.now()
            receipt.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Receipt sent to {receipt.customer_email}'
            })
            
        except Exception as e:
            logger.error(f"Error sending POS receipt email: {str(e)}")
            return JsonResponse({'error': 'Failed to send email'}, status=500)
