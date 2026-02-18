from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid
import os

def get_upload_path(instance, filename):
    """Generate upload path for rider documents"""
    return f"riders/{instance.user.id}/{filename}"

class RiderProfile(models.Model):
    """Rider profile with approval status and delivery information"""
    
    VEHICLE_TYPES = (
        ('bicycle', 'Bicycle'),
        ('motorcycle', 'Motorcycle'),
        ('car', 'Car'),
    )
    
    APPROVAL_STATUS = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='rider_profile'
    )
    
    # Personal Information
    id_number = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]+$',
                message='ID number should only contain alphanumeric characters'
            )
        ]
    )
    id_document = models.FileField(
        upload_to=get_upload_path,
        help_text='Upload a clear photo of your ID document'
    )
    
    # Vehicle Information
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPES,
        default='motorcycle'
    )
    vehicle_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9-]+$',
                message='Vehicle number should only contain alphanumeric characters and hyphens'
            )
        ]
    )
    vehicle_document = models.FileField(
        upload_to=get_upload_path,
        help_text='Upload vehicle registration document'
    )
    
    # Contact Information
    emergency_contact = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[0-9+\s-]+$',
                message='Emergency contact should only contain numbers, spaces, hyphens, and plus sign'
            )
        ],
        help_text='Emergency contact phone number'
    )
    
    # Banking Information
    bank_account = models.CharField(
        max_length=50,
        help_text='Bank account number for payments'
    )
    bank_name = models.CharField(
        max_length=100,
        help_text='Bank name'
    )
    
    # Delivery Information
    delivery_areas = models.JSONField(
        default=list,
        help_text='List of areas where rider can deliver'
    )
    
    # Performance Metrics
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        help_text='Average rating from customers'
    )
    total_deliveries = models.IntegerField(
        default=0,
        help_text='Total number of completed deliveries'
    )
    
    # Status
    is_online = models.BooleanField(
        default=False,
        help_text='Whether rider is currently available for deliveries'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether rider account is active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Rider Profile"
        verbose_name_plural = "Rider Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_approval_status_display()}"
    
    @property
    def approval_status(self):
        """Get approval status from user model"""
        return getattr(self.user, 'approval_status', 'pending')
    
    @property
    def is_approved(self):
        """Check if rider is approved"""
        return getattr(self.user, 'is_approved', False)
    
    def get_approval_status_display(self):
        """Get human-readable approval status"""
        status_map = {
            'pending': 'Pending Approval',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'suspended': 'Suspended'
        }
        return status_map.get(self.approval_status, 'Unknown')
    
    def update_last_active(self):
        """Update last active timestamp"""
        from django.utils import timezone
        self.last_active_at = timezone.now()
        self.save(update_fields=['last_active_at'])
    
    def calculate_earnings(self, start_date=None, end_date=None):
        """Calculate rider earnings for a date range"""
        from django.db.models import Sum
        from decimal import Decimal
        from .models import DeliveryAssignment
        
        deliveries = DeliveryAssignment.objects.filter(
            rider=self,
            status='delivered'
        )
        
        if start_date:
            deliveries = deliveries.filter(delivered_at__gte=start_date)
        if end_date:
            deliveries = deliveries.filter(delivered_at__lte=end_date)
        
        total_earnings = deliveries.aggregate(
            total=Sum('delivery_fee')
        )['total'] or Decimal('0.00')
        
        return total_earnings


class DeliveryAssignment(models.Model):
    """Assignment of orders to riders for delivery"""
    
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='delivery_assignments'
    )
    rider = models.ForeignKey(
        RiderProfile,
        on_delete=models.CASCADE,
        related_name='delivery_assignments'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned'
    )
    
    # Financial Information
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Delivery fee for this assignment'
    )
    
    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes and tracking
    pickup_notes = models.TextField(
        blank=True,
        help_text='Notes about pickup'
    )
    delivery_notes = models.TextField(
        blank=True,
        help_text='Notes about delivery'
    )
    
    # Location tracking (can be extended with GPS coordinates)
    pickup_location = models.JSONField(
        null=True,
        blank=True,
        help_text='Pickup location coordinates'
    )
    delivery_location = models.JSONField(
        null=True,
        blank=True,
        help_text='Delivery location coordinates'
    )
    
    class Meta:
        verbose_name = "Delivery Assignment"
        verbose_name_plural = "Delivery Assignments"
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"Order #{self.order.id} - {self.rider.user.get_full_name()}"
    
    def get_status_display(self):
        """Get human-readable status"""
        status_map = {
            'assigned': 'Assigned',
            'picked_up': 'Picked Up',
            'delivering': 'Delivering',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled',
            'failed': 'Failed'
        }
        return status_map.get(self.status, 'Unknown')
    
    def mark_picked_up(self):
        """Mark assignment as picked up"""
        from django.utils import timezone
        self.status = 'picked_up'
        self.picked_up_at = timezone.now()
        self.save()
    
    def mark_delivered(self):
        """Mark assignment as delivered"""
        from django.utils import timezone
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
        
        # Update rider stats
        self.rider.total_deliveries += 1
        self.rider.save(update_fields=['total_deliveries'])
    
    def cancel_assignment(self, reason=""):
        """Cancel the assignment"""
        self.status = 'cancelled'
        self.delivery_notes = f"Cancelled: {reason}"
        self.save()


class RiderEarning(models.Model):
    """Track rider warnings and disciplinary actions"""
    
    WARNING_TYPES = (
        ('late_delivery', 'Late Delivery'),
        ('customer_complaint', 'Customer Complaint'),
        ('order_cancellation', 'Order Cancellation'),
        ('policy_violation', 'Policy Violation'),
        ('other', 'Other'),
    )
    
    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(
        RiderProfile,
        on_delete=models.CASCADE,
        related_name='warnings'
    )
    
    warning_type = models.CharField(
        max_length=20,
        choices=WARNING_TYPES
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='medium'
    )
    
    description = models.TextField()
    evidence = models.FileField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        help_text='Supporting evidence if any'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_warnings'
    )
    
    class Meta:
        verbose_name = "Rider Warning"
        verbose_name_plural = "Rider Warnings"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rider.user.get_full_name()} - {self.get_warning_type_display()}"
