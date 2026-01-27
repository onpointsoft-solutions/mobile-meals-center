from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import Order, OrderItem
from .forms import OrderForm, OrderStatusForm
from meals.models import Meal
from decimal import Decimal


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
        
        messages.success(request, f'{meal.name} added to cart!')
        return redirect('orders:cart')


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
        order = get_object_or_404(Order, pk=pk)
        form = OrderStatusForm(request.POST, instance=order)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated successfully!')
        else:
            messages.error(request, 'Error updating order status.')
        
        return redirect('orders:detail', pk=order.pk)
