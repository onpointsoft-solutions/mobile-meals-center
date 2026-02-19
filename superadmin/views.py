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
from restaurants.models_pos import POSSession, POSOrder, POSOrderItem
from meals.models import Meal, Category
from orders.models import Order, OrderItem
from riders.models import RiderProfile
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
        context['total_riders'] = User.objects.filter(user_type='rider').count()
        context['pending_riders'] = User.objects.filter(user_type='rider', is_approved=False).count()
        context['approved_riders'] = User.objects.filter(user_type='rider', is_approved=True).count()
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
        
        return redirect('superadmin:complaint_detail', pk=complaint.pk)


class POSManagementView(SuperAdminRequiredMixin, TemplateView):
    """POS system management dashboard"""
    template_name = 'superadmin/pos_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get POS statistics
        total_restaurants = Restaurant.objects.count()
        pos_enabled_restaurants = Restaurant.objects.filter(pos_enabled=True).count()
        pos_disabled_restaurants = total_restaurants - pos_enabled_restaurants
        
        # Get active POS sessions
        active_sessions = POSSession.objects.filter(is_active=True).count()
        
        # Get today's POS sales
        from django.utils import timezone
        today = timezone.now().date()
        today_pos_orders = POSOrder.objects.filter(
            created_at__date=today,
            status='completed'
        )
        today_sales = today_pos_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        today_order_count = today_pos_orders.count()
        
        # Get top restaurants by POS sales
        top_restaurants = Restaurant.objects.annotate(
            pos_sales=Sum('pos_orders__total_amount', filter=Q(
                pos_orders__status='completed',
                pos_orders__created_at__date=today
            ))
        ).order_by('-pos_sales')[:10]
        
        # Recent POS sessions
        recent_sessions = POSSession.objects.select_related('restaurant', 'opened_by').order_by('-opened_at')[:10]
        
        context.update({
            'total_restaurants': total_restaurants,
            'pos_enabled_restaurants': pos_enabled_restaurants,
            'pos_disabled_restaurants': pos_disabled_restaurants,
            'active_sessions': active_sessions,
            'today_sales': today_sales,
            'today_order_count': today_order_count,
            'top_restaurants': top_restaurants,
            'recent_sessions': recent_sessions,
        })
        return context


class POSToggleView(SuperAdminRequiredMixin, View):
    """Toggle POS access for a restaurant"""
    
    def post(self, request):
        restaurant_id = request.POST.get('restaurant_id')
        action = request.POST.get('action')  # 'enable' or 'disable'
        
        if not restaurant_id or action not in ['enable', 'disable']:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        old_status = restaurant.pos_enabled
        new_status = action == 'enable'
        
        if old_status == new_status:
            return JsonResponse({'error': f'POS is already {"enabled" if new_status else "disabled"}'}, status=400)
        
        restaurant.pos_enabled = new_status
        restaurant.save()
        
        # Log activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='update',
            target_model='Restaurant',
            target_id=restaurant.id,
            description=f'{"Enabled" if new_status else "Disabled"} POS access for restaurant: {restaurant.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({
            'success': True,
            'message': f'POS {"enabled" if new_status else "disabled"} for {restaurant.name}',
            'new_status': new_status
        })


class POSRestaurantsView(SuperAdminRequiredMixin, ListView):
    """List all restaurants with POS settings"""
    model = Restaurant
    template_name = 'superadmin/pos_restaurants.html'
    context_object_name = 'restaurants'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Restaurant.objects.select_related('owner').annotate(
            pos_order_count=Count('pos_orders'),
            pos_sales=Sum('pos_orders__total_amount', filter=Q(pos_orders__status='completed'))
        ).order_by('-created_at')
        
        # Filter by POS status
        pos_status = self.request.GET.get('pos_status')
        if pos_status == 'enabled':
            queryset = queryset.filter(pos_enabled=True)
        elif pos_status == 'disabled':
            queryset = queryset.filter(pos_enabled=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_restaurants'] = Restaurant.objects.count()
        context['enabled_count'] = Restaurant.objects.filter(pos_enabled=True).count()
        context['disabled_count'] = Restaurant.objects.filter(pos_enabled=False).count()
        
        return context


class POSSessionsView(SuperAdminRequiredMixin, ListView):
    """List all POS sessions"""
    model = POSSession
    template_name = 'superadmin/pos_sessions.html'
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        return POSSession.objects.select_related('restaurant', 'opened_by').order_by('-opened_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_sessions'] = POSSession.objects.count()
        context['active_sessions'] = POSSession.objects.filter(is_active=True).count()
        total_sales = POSSession.objects.aggregate(
            cash_total=Sum('cash_sales'),
            card_total=Sum('card_sales'),
            mpesa_total=Sum('mpesa_sales')
        )
        context['total_sales'] = (
            (total_sales['cash_total'] or Decimal('0.00')) +
            (total_sales['card_total'] or Decimal('0.00')) +
            (total_sales['mpesa_total'] or Decimal('0.00'))
        )
        
        return context


class FinancialSettingsView(SuperAdminRequiredMixin, TemplateView):
    """Manage financial settings like delivery fee and commission"""
    template_name = 'superadmin/financial_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from core.utils import get_delivery_fee, get_commission_rate, get_tax_rate
        
        # Calculate example values for display
        example_order_amount = Decimal('1000.00')
        example_subtotal = example_order_amount + get_delivery_fee()
        example_tax = example_subtotal * (get_tax_rate() / Decimal('100'))
        example_total = example_subtotal + example_tax
        example_commission = example_order_amount * (get_commission_rate() / Decimal('100'))
        example_net_to_restaurant = example_order_amount - example_commission
        
        context.update({
            'delivery_fee': get_delivery_fee(),
            'commission_rate': get_commission_rate(),
            'tax_rate': get_tax_rate(),
            'example_order_amount': example_order_amount,
            'example_subtotal': example_subtotal,
            'example_tax': example_tax,
            'example_total': example_total,
            'example_commission': example_commission,
            'example_net_to_restaurant': example_net_to_restaurant,
        })
        
        return context
    
    def post(self, request):
        delivery_fee = request.POST.get('delivery_fee')
        commission_rate = request.POST.get('commission_rate')
        tax_rate = request.POST.get('tax_rate')
        
        # Validate inputs
        try:
            delivery_fee = float(delivery_fee)
            commission_rate = float(commission_rate)
            tax_rate = float(tax_rate)
            
            if delivery_fee < 0 or commission_rate < 0 or tax_rate < 0:
                raise ValueError("Values must be positive")
            
            if commission_rate > 100 or tax_rate > 100:
                raise ValueError("Rates cannot exceed 100%")
                
        except (ValueError, TypeError) as e:
            messages.error(request, f'Invalid input: {str(e)}')
            return redirect('superadmin:financial_settings')
        
        # Update settings
        from superadmin.models import SystemSettings
        from core.utils import clear_system_settings_cache
        
        settings_updated = []
        
        for key, value in [
            ('delivery_fee', str(delivery_fee)),
            ('commission_rate', str(commission_rate)),
            ('tax_rate', str(tax_rate)),
        ]:
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': self._get_setting_description(key)}
            )
            
            if not created:
                setting.value = value
                setting.updated_by = request.user
                setting.save()
            
            settings_updated.append(key)
        
        # Clear cache
        clear_system_settings_cache()
        
        # Log activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='update',
            target_model='SystemSettings',
            target_id=0,
            description=f'Updated financial settings: {", ".join(settings_updated)}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Financial settings updated successfully!')
        return redirect('superadmin:financial_settings')
    
    def _get_setting_description(self, key):
        descriptions = {
            'delivery_fee': 'Delivery fee charged to customers for online orders',
            'commission_rate': 'Commission percentage charged to restaurants (percentage)',
            'tax_rate': 'Tax rate applied to orders (percentage)',
        }
        return descriptions.get(key, '')


# Rider Management Views

class RiderManagementView(SuperAdminRequiredMixin, ListView):
    """View to manage all riders"""
    model = RiderProfile
    template_name = 'superadmin/rider_management.html'
    context_object_name = 'riders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = RiderProfile.objects.select_related('user').order_by('-created_at')
        
        # Filter by approval status
        status_filter = self.request.GET.get('status')
        if status_filter:
            if status_filter == 'pending':
                queryset = queryset.filter(user__is_approved=False)
            elif status_filter == 'approved':
                queryset = queryset.filter(user__is_approved=True)
            elif status_filter == 'rejected':
                queryset = queryset.filter(user__approval_status='rejected')
        
        # Search by username or email
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_riders'] = RiderProfile.objects.count()
        context['pending_riders'] = RiderProfile.objects.filter(user__is_approved=False).count()
        context['approved_riders'] = RiderProfile.objects.filter(user__is_approved=True).count()
        context['rejected_riders'] = RiderProfile.objects.filter(user__approval_status='rejected').count()
        return context


class RiderDetailView(SuperAdminRequiredMixin, DetailView):
    """View to see rider details"""
    model = RiderProfile
    template_name = 'superadmin/rider_detail.html'
    context_object_name = 'rider'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rider = self.get_object()
        
        # Get rider's delivery statistics
        from riders.models import DeliveryAssignment
        context['total_deliveries'] = DeliveryAssignment.objects.filter(
            rider=rider, status='delivered'
        ).count()
        context['active_deliveries'] = DeliveryAssignment.objects.filter(
            rider=rider, status__in=['assigned', 'picked_up', 'delivering']
        ).count()
        
        return context


class ApproveRiderView(SuperAdminRequiredMixin, View):
    """View to approve a rider"""
    
    def post(self, request, pk):
        rider = get_object_or_404(RiderProfile, pk=pk)
        user = rider.user
        
        if user.is_approved:
            messages.warning(request, 'Rider is already approved.')
        else:
            # Approve the rider
            user.is_approved = True
            user.approval_status = 'approved'
            user.save()
            
            # Activate the rider profile
            rider.is_active = True
            rider.save()
            
            # Log activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action='approve',
                target_model='RiderProfile',
                target_id=rider.id,
                description=f'Approved rider: {user.get_full_name() or user.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Rider {user.get_full_name() or user.username} has been approved successfully!')
        
        return redirect('superadmin:rider_detail', pk=rider.pk)


class RejectRiderView(SuperAdminRequiredMixin, View):
    """View to reject a rider"""
    
    def post(self, request, pk):
        rider = get_object_or_404(RiderProfile, pk=pk)
        user = rider.user
        
        if user.approval_status == 'rejected':
            messages.warning(request, 'Rider is already rejected.')
        else:
            # Reject the rider
            user.is_approved = False
            user.approval_status = 'rejected'
            user.save()
            
            # Deactivate the rider profile
            rider.is_active = False
            rider.save()
            
            # Log activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action='reject',
                target_model='RiderProfile',
                target_id=rider.id,
                description=f'Rejected rider: {user.get_full_name() or user.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Rider {user.get_full_name() or user.username} has been rejected.')
        
        return redirect('superadmin:rider_detail', pk=rider.pk)


class ToggleRiderStatusView(SuperAdminRequiredMixin, View):
    """View to toggle rider active status"""
    
    def post(self, request, pk):
        rider = get_object_or_404(RiderProfile, pk=pk)
        
        # Toggle active status
        rider.is_active = not rider.is_active
        rider.save()
        
        status_text = "activated" if rider.is_active else "deactivated"
        
        # Log activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='toggle_status',
            target_model='RiderProfile',
            target_id=rider.id,
            description=f'{status_text.capitalize()} rider: {rider.user.get_full_name() or rider.user.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Rider {rider.user.get_full_name() or rider.user.username} has been {status_text}.')
        return redirect('superadmin:rider_detail', pk=rider.pk)
