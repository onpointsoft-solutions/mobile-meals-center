from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from .models import RiderProfile, DeliveryAssignment, RiderEarning

@admin.register(RiderProfile)
class RiderProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'approval_status', 'vehicle_type', 
        'rating', 'total_deliveries', 'is_online', 'created_at'
    ]
    list_filter = [
        'user__approval_status', 'vehicle_type', 'is_online', 
        'is_active', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__first_name', 
        'user__last_name', 'vehicle_number', 'id_number'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'total_deliveries', 'rating'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'id_number', 'id_document', 'emergency_contact')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_number', 'vehicle_document')
        }),
        ('Banking Information', {
            'fields': ('bank_account', 'bank_name')
        }),
        ('Delivery Information', {
            'fields': ('delivery_areas', 'is_online', 'is_active')
        }),
        ('Performance Metrics', {
            'fields': ('rating', 'total_deliveries'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'last_active_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_riders', 'reject_riders', 'suspend_riders', 'activate_riders']
    
    def approval_status(self, obj):
        """Display approval status with color coding"""
        status = obj.approval_status
        colors = {
            'pending': '#FFA500',  # Orange
            'approved': '#4CAF50',  # Green
            'rejected': '#F44336',  # Red
            'suspended': '#9E9E9E'  # Gray
        }
        color = colors.get(status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_approval_status_display()
        )
    approval_status.short_description = 'Approval Status'
    
    def user(self, obj):
        """Display user with link to user admin"""
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:accounts_user_change', args=[obj.user.id]),
                obj.user.get_full_name() or obj.user.username
            )
        return "-"
    user.short_description = 'User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'rider', 'status', 'delivery_fee',
        'assigned_at', 'picked_up_at', 'delivered_at'
    ]
    list_filter = [
        'status', 'assigned_at', 'picked_up_at', 'delivered_at'
    ]
    search_fields = [
        'order__id', 'order__customer__first_name',
        'order__customer__last_name', 'rider__user__first_name',
        'rider__user__last_name', 'vehicle_number'
    ]
    readonly_fields = [
        'id', 'assigned_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('order', 'rider', 'status', 'delivery_fee')
        }),
        ('Timestamps', {
            'fields': ('assigned_at', 'picked_up_at', 'delivered_at')
        }),
        ('Location Tracking', {
            'fields': ('pickup_location', 'delivery_location'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('pickup_notes', 'delivery_notes'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_picked_up', 'mark_delivered', 'cancel_assignments']
    
    def order(self, obj):
        """Display order with link"""
        if obj.order:
            return format_html(
                '<a href="{}">#{}</a>',
                reverse('admin:orders_order_change', args=[obj.order.id]),
                obj.order.id
            )
        return "-"
    order.short_description = 'Order'
    
    def rider(self, obj):
        """Display rider with link"""
        if obj.rider:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:riders_riderprofile_change', args=[obj.rider.id]),
                obj.rider.user.get_full_name() or obj.rider.user.username
            )
        return "-"
    rider.short_description = 'Rider'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'rider', 'rider__user'
        )


@admin.register(RiderEarning)
class RiderWarningAdmin(admin.ModelAdmin):
    list_display = [
        'rider', 'warning_type', 'severity', 
        'description', 'created_at', 'created_by'
    ]
    list_filter = [
        'warning_type', 'severity', 'created_at'
    ]
    search_fields = [
        'rider__user__first_name', 'rider__user__last_name',
        'description'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Warning Information', {
            'fields': ('rider', 'warning_type', 'severity', 'description')
        }),
        ('Evidence', {
            'fields': ('evidence',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'created_by')
        })
    )
    
    def rider(self, obj):
        """Display rider with link"""
        if obj.rider:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:riders_riderprofile_change', args=[obj.rider.id]),
                obj.rider.user.get_full_name() or obj.rider.user.username
            )
        return "-"
    rider.short_description = 'Rider'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'rider', 'rider__user', 'created_by'
        )


# Extend UserAdmin to show rider profile link
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('rider_profile_link',)
    
    def rider_profile_link(self, obj):
        """Add link to rider profile if user is a rider"""
        try:
            rider_profile = obj.rider_profile
            if rider_profile:
                return format_html(
                    '<a href="{}">View Rider Profile</a>',
                    reverse('admin:riders_riderprofile_change', args=[rider_profile.id])
                )
        except RiderProfile.DoesNotExist:
            pass
        return "-"
    rider_profile_link.short_description = 'Rider Profile'


# Unregister default UserAdmin and register custom one
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
User = settings.AUTH_USER_MODEL
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
