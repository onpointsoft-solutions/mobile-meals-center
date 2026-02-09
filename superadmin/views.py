from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, TemplateView, View, CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from restaurants.models import Restaurant
from meals.models import Meal, Category
from orders.models import Order, OrderItem
from .models import AdminActivityLog, SystemSettings, Complaint
from .forms import SuperAdminLoginForm


class SuperAdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only superusers can access"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('core:home')


class AdminDashboardView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'superadmin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Overall statistics
        context['total_users'] = User.objects.count()
        context['total_customers'] = User.objects.filter(user_type='customer').count()
        context['total_restaurants'] = Restaurant.objects.count()
        context['active_restaurants'] = Restaurant.objects.filter(is_active=True).count()
        context['total_meals'] = Meal.objects.count()
        context['available_meals'] = Meal.objects.filter(is_available=True).count()
        context['total_orders'] = Order.objects.count()
        context['total_revenue'] = Order.objects.filter(
            status__in=['confirmed', 'preparing', 'ready', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Recent statistics
        context['new_users_week'] = User.objects.filter(date_joined__gte=week_ago).count()
        context['new_restaurants_week'] = Restaurant.objects.filter(created_at__gte=week_ago).count()
        context['orders_week'] = Order.objects.filter(created_at__gte=week_ago).count()
        context['revenue_week'] = Order.objects.filter(
            created_at__gte=week_ago,
            status__in=['confirmed', 'preparing', 'ready', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Order status breakdown
        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['confirmed_orders'] = Order.objects.filter(status='confirmed').count()
        context['preparing_orders'] = Order.objects.filter(status='preparing').count()
        context['ready_orders'] = Order.objects.filter(status='ready').count()
        context['delivered_orders'] = Order.objects.filter(status='delivered').count()
        context['cancelled_orders'] = Order.objects.filter(status='cancelled').count()
        
        # Top restaurants by orders
        context['top_restaurants'] = Restaurant.objects.annotate(
            order_count=Count('orders')
        ).order_by('-order_count')[:5]
        
        # Top meals by orders
        context['top_meals'] = Meal.objects.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:5]
        
        # Recent activity
        context['recent_orders'] = Order.objects.select_related(
            'customer', 'restaurant'
        ).order_by('-created_at')[:10]
        
        context['recent_users'] = User.objects.order_by('-date_joined')[:10]
        
        context['recent_logs'] = AdminActivityLog.objects.select_related(
            'admin'
        ).order_by('-created_at')[:10]
        
        return context


class RestaurantManagementView(SuperAdminRequiredMixin, ListView):
    model = Restaurant
    template_name = 'superadmin/restaurants.html'
    context_object_name = 'restaurants'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Restaurant.objects.select_related('owner').annotate(
            meal_count=Count('meals'),
            order_count=Count('orders'),
            total_revenue=Sum('orders__total_amount', filter=Q(
                orders__status__in=['confirmed', 'preparing', 'ready', 'delivered']
            ))
        )
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(owner__username__icontains=search) |
                Q(owner__email__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-created_at')


class RestaurantDetailAdminView(SuperAdminRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'superadmin/restaurant_detail.html'
    context_object_name = 'restaurant'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.object
        
        context['meals'] = restaurant.meals.all()
        context['orders'] = restaurant.orders.select_related('customer').order_by('-created_at')[:20]
        context['total_orders'] = restaurant.orders.count()
        context['total_revenue'] = restaurant.orders.filter(
            status__in=['confirmed', 'preparing', 'ready', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        return context


class UserManagementView(SuperAdminRequiredMixin, ListView):
    model = User
    template_name = 'superadmin/users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filter by type
        user_type = self.request.GET.get('type')
        if user_type == 'customer':
            queryset = queryset.filter(is_customer=True)
        elif user_type == 'restaurant':
            queryset = queryset.filter(is_restaurant=True)
        elif user_type == 'admin':
            queryset = queryset.filter(is_superuser=True)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-date_joined')


class OrderManagementView(SuperAdminRequiredMixin, ListView):
    model = Order
    template_name = 'superadmin/orders.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Order.objects.select_related('customer', 'restaurant')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(customer__username__icontains=search) |
                Q(restaurant__name__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


class ToggleRestaurantStatusView(SuperAdminRequiredMixin, DetailView):
    model = Restaurant
    
    def post(self, request, *args, **kwargs):
        restaurant = self.get_object()
        restaurant.is_active = not restaurant.is_active
        restaurant.save()
        
        # Log activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='activate' if restaurant.is_active else 'suspend',
            target_model='Restaurant',
            target_id=restaurant.id,
            description=f"{'Activated' if restaurant.is_active else 'Suspended'} restaurant: {restaurant.name}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        status = 'activated' if restaurant.is_active else 'suspended'
        messages.success(request, f'Restaurant {restaurant.name} has been {status}.')
        
        return redirect('superadmin:restaurant_detail', pk=restaurant.pk)


class ToggleUserStatusView(SuperAdminRequiredMixin, DetailView):
    model = User
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        
        if user.is_superuser:
            messages.error(request, 'Cannot modify superuser accounts.')
            return redirect('superadmin:users')
        
        user.is_active = not user.is_active
        user.save()
        
        # Log activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='activate' if user.is_active else 'suspend',
            target_model='User',
            target_id=user.id,
            description=f"{'Activated' if user.is_active else 'Suspended'} user: {user.username}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        status = 'activated' if user.is_active else 'suspended'
        messages.success(request, f'User {user.username} has been {status}.')
        
        return redirect('superadmin:users')


class CategoryManagementView(SuperAdminRequiredMixin, ListView):
    model = Category
    template_name = 'superadmin/categories.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.annotate(
            meal_count=Count('meal')
        ).order_by('name')


class SystemSettingsView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'superadmin/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = SystemSettings.objects.all()
        return context


class ActivityLogView(SuperAdminRequiredMixin, ListView):
    model = AdminActivityLog
    template_name = 'superadmin/activity_log.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        return AdminActivityLog.objects.select_related('admin').order_by('-created_at')


class SuperAdminLoginView(LoginView):
    template_name = 'superadmin/login.html'
    form_class = SuperAdminLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('superadmin:dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser:
            messages.error(self.request, 'You do not have permission to access the admin panel.')
            return redirect('core:home')
        
        # Log the login
        AdminActivityLog.objects.create(
            admin=user,
            action='update',
            target_model='User',
            target_id=user.id,
            description=f'Admin login: {user.username}',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        return super().form_valid(form)


class SuperAdminLogoutView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            AdminActivityLog.objects.create(
                admin=request.user,
                action='update',
                target_model='User',
                target_id=request.user.id,
                description=f'Admin logout: {request.user.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('superadmin:login')


class ComplaintManagementView(SuperAdminRequiredMixin, ListView):
    model = Complaint
    template_name = 'superadmin/complaints.html'
    context_object_name = 'complaints'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Complaint.objects.select_related('user', 'resolved_by')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(description__icontains=search) |
                Q(user__username__icontains=search) |
                Q(order_number__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')


class ComplaintDetailView(SuperAdminRequiredMixin, DetailView):
    model = Complaint
    template_name = 'superadmin/complaint_detail.html'
    context_object_name = 'complaint'


class UpdateComplaintStatusView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if new_status in dict(Complaint.STATUS_CHOICES):
            old_status = complaint.status
            complaint.status = new_status
            
            if admin_notes:
                complaint.admin_notes = admin_notes
            
            if new_status == 'resolved':
                complaint.mark_resolved(request.user)
            else:
                complaint.save()
            
            # Log activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action='update',
                target_model='Complaint',
                target_id=complaint.id,
                description=f'Updated complaint status from {old_status} to {new_status}: {complaint.subject}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Complaint status updated to {complaint.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
        
        return redirect('superadmin:complaint_detail', pk=pk)
