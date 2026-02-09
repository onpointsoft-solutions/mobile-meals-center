from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal
import logging
from .models import Order, OrderItem
from .forms import OrderForm
from meals.models import Meal

logger = logging.getLogger(__name__)

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        if user.is_restaurant:
            return Order.objects.filter(restaurant=user.restaurant)
        else:
            return Order.objects.filter(customer=user)


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    
    def test_func(self):
        order = self.get_object()
        user = self.request.user
        return user == order.customer or (user.is_restaurant and user.restaurant == order.restaurant)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Calculate order totals
        subtotal = order.total_amount
        delivery_fee = Decimal('3.99')
        subtotal_with_delivery = subtotal + delivery_fee
        tax_amount = subtotal_with_delivery * Decimal('0.08')
        final_total = subtotal_with_delivery + tax_amount
        
        context['delivery_fee'] = delivery_fee
        context['tax_amount'] = tax_amount
        context['final_total'] = final_total
        
        return context


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        cart_items = []
        total = Decimal('0.00')
        
        for meal_id, quantity in cart.items():
            try:
                meal = Meal.objects.get(id=meal_id, is_available=True)
                item_total = meal.price * quantity
                cart_items.append({
                    'meal': meal,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
            except Meal.DoesNotExist:
                pass
        
        context['cart_items'] = cart_items
        context['total'] = total
        return context


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, meal_id):
        meal = get_object_or_404(Meal, id=meal_id, is_available=True)
        quantity = int(request.POST.get('quantity', 1))
        
        cart = request.session.get('cart', {})
        cart[str(meal_id)] = cart.get(str(meal_id), 0) + quantity
        request.session['cart'] = cart
        
        logger.info(f'Added {quantity} of meal {meal_id} to cart for user {request.user.username}')
        messages.success(request, f'{meal.name} added to cart!')
        return redirect('orders:cart')


class UpdateCartView(LoginRequiredMixin, View):
    """Update quantity of item in cart via AJAX"""
    def post(self, request, meal_id):
        try:
            meal = get_object_or_404(Meal, id=meal_id, is_available=True)
            action = request.POST.get('action', 'set')  # 'set', 'increment', 'decrement'
            
            cart = request.session.get('cart', {})
            meal_id_str = str(meal_id)
            
            if action == 'increment':
                cart[meal_id_str] = cart.get(meal_id_str, 0) + 1
            elif action == 'decrement':
                current_qty = cart.get(meal_id_str, 0)
                if current_qty > 1:
                    cart[meal_id_str] = current_qty - 1
                else:
                    # Remove item if quantity would be 0
                    cart.pop(meal_id_str, None)
            else:  # set
                quantity = int(request.POST.get('quantity', 1))
                if quantity > 0:
                    cart[meal_id_str] = quantity
                else:
                    cart.pop(meal_id_str, None)
            
            request.session['cart'] = cart
            request.session.modified = True
            
            # Calculate new totals
            cart_total = Decimal('0.00')
            cart_count = 0
            for mid, qty in cart.items():
                try:
                    m = Meal.objects.get(id=mid, is_available=True)
                    cart_total += m.price * qty
                    cart_count += qty
                except Meal.DoesNotExist:
                    pass
            
            item_quantity = cart.get(meal_id_str, 0)
            item_total = meal.price * item_quantity if item_quantity > 0 else Decimal('0.00')
            
            logger.info(f'Updated cart for user {request.user.username}: meal {meal_id}, action {action}')
            
            return JsonResponse({
                'success': True,
                'item_quantity': item_quantity,
                'item_total': float(item_total),
                'cart_total': float(cart_total),
                'cart_count': cart_count,
                'message': 'Cart updated successfully'
            })
            
        except Exception as e:
            logger.error(f'Error updating cart: {str(e)}')
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)


class RemoveFromCartView(LoginRequiredMixin, View):
    """Remove item from cart"""
    def post(self, request, meal_id):
        try:
            cart = request.session.get('cart', {})
            meal_id_str = str(meal_id)
            
            if meal_id_str in cart:
                del cart[meal_id_str]
                request.session['cart'] = cart
                request.session.modified = True
                
                # Calculate new totals
                cart_total = Decimal('0.00')
                cart_count = 0
                for mid, qty in cart.items():
                    try:
                        m = Meal.objects.get(id=mid, is_available=True)
                        cart_total += m.price * qty
                        cart_count += qty
                    except Meal.DoesNotExist:
                        pass
                
                logger.info(f'Removed meal {meal_id} from cart for user {request.user.username}')
                
                return JsonResponse({
                    'success': True,
                    'cart_total': float(cart_total),
                    'cart_count': cart_count,
                    'message': 'Item removed from cart'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Item not found in cart'
                }, status=404)
                
        except Exception as e:
            logger.error(f'Error removing from cart: {str(e)}')
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/create.html'
    success_url = reverse_lazy('orders:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        cart_items = []
        total = Decimal('0.00')
        
        for meal_id, quantity in cart.items():
            try:
                meal = Meal.objects.get(id=meal_id, is_available=True)
                item_total = meal.price * quantity
                cart_items.append({
                    'meal': meal,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
            except Meal.DoesNotExist:
                pass
        
        context['cart_items'] = cart_items
        context['total'] = total
        return context
    
    def form_valid(self, form):
        cart = self.request.session.get('cart', {})
        if not cart:
            messages.error(self.request, 'Your cart is empty!')
            return redirect('orders:cart')
        
        with transaction.atomic():
            # Get the first meal's restaurant (assuming single restaurant per order)
            first_meal_id = list(cart.keys())[0]
            first_meal = Meal.objects.get(id=first_meal_id)
            
            form.instance.customer = self.request.user
            form.instance.restaurant = first_meal.restaurant
            
            # Calculate total
            total = Decimal('0.00')
            for meal_id, quantity in cart.items():
                meal = Meal.objects.get(id=meal_id, is_available=True)
                total += meal.price * quantity
            
            form.instance.total_amount = total
            order = form.save()
            
            # Create order items
            for meal_id, quantity in cart.items():
                meal = Meal.objects.get(id=meal_id, is_available=True)
                OrderItem.objects.create(
                    order=order,
                    meal=meal,
                    quantity=quantity,
                    price=meal.price
                )
            
            # Clear cart
            del self.request.session['cart']
            
            messages.success(self.request, f'Order #{order.order_number} created successfully! Please complete payment.')
            return redirect('payments:process_payment', order_id=order.pk)


class UpdateOrderStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        return self.request.user.is_restaurant and self.request.user.restaurant == order.restaurant
    
    def post(self, request, pk):
        try:
            order = get_object_or_404(Order, pk=pk)
            new_status = request.POST.get('status')
            
            if new_status in dict(Order.STATUS_CHOICES):
                old_status = order.status
                order.status = new_status
                order.save()
                
                logger.info(f'Order {order.order_number} status updated from {old_status} to {new_status} by {request.user.username}')
                
                # Return JSON response for AJAX calls
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'Order status updated to {order.get_status_display()}',
                        'new_status': new_status,
                        'new_status_display': order.get_status_display()
                    })
                
                messages.success(request, f'Order status updated to {order.get_status_display()}')
                return redirect('orders:detail', pk=pk)
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid status'
                    }, status=400)
                
                messages.error(request, 'Invalid status')
                return redirect('orders:detail', pk=pk)
                
        except Exception as e:
            logger.error(f'Error updating order status: {str(e)}')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            
            messages.error(request, 'Failed to update order status')
            return redirect('orders:detail', pk=pk)
