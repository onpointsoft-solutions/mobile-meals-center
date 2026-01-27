from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, UserProfileForm
from restaurants.models import Restaurant
from orders.models import Order


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Registration successful!')
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_restaurant:
            try:
                restaurant = user.restaurant
                context['restaurant'] = restaurant
                context['recent_orders'] = Order.objects.filter(restaurant=restaurant)[:5]
                context['total_orders'] = Order.objects.filter(restaurant=restaurant).count()
                context['pending_orders'] = Order.objects.filter(
                    restaurant=restaurant, status='pending'
                ).count()
            except Restaurant.DoesNotExist:
                context['needs_restaurant_profile'] = True
        else:
            context['recent_orders'] = Order.objects.filter(customer=user)[:5]
            context['total_orders'] = Order.objects.filter(customer=user).count()
        
        return context


class CustomLogoutView(View):
    """Custom logout view with session cleanup and smart redirection"""
    
    def get(self, request):
        return self.logout_user(request)
    
    def post(self, request):
        return self.logout_user(request)
    
    def logout_user(self, request):
        if request.user.is_authenticated:
            # Store user type before logout for smart redirection
            was_restaurant = request.user.is_restaurant
            
            # Clear cart session data
            if 'cart' in request.session:
                del request.session['cart']
            
            # Logout the user
            logout(request)
            
            # Add success message
            messages.success(request, 'You have been successfully logged out.')
            
            # Smart redirection based on user type
            # Restaurants go to home, customers can go to browse meals
            if was_restaurant:
                return redirect('core:home')
            else:
                # Get next parameter if provided
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('core:home')
        else:
            # User already logged out
            return redirect('core:home')
