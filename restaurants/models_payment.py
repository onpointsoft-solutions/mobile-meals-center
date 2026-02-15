from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class RestaurantPaymentProfile(models.Model):
    """Store restaurant payment details for payouts"""
    
    PAYOUT_METHODS = (
        ('bank_transfer', 'Bank Transfer'),
        ('paystack', 'Paystack Transfer'),
    )
    
    BANK_TYPES = (
        ('individual', 'Individual Account'),
        ('business', 'Business Account'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.OneToOneField(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='payment_profile'
    )
    
    # Payout method preference
    payout_method = models.CharField(
        max_length=20, 
        choices=PAYOUT_METHODS, 
        default='bank_transfer'
    )
    
    # Bank details for transfers
    bank_name = models.CharField(max_length=100, blank=True)
    bank_code = models.CharField(max_length=10, blank=True)  # Nigerian bank codes
    account_number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    account_type = models.CharField(
        max_length=20, 
        choices=BANK_TYPES, 
        default='individual',
        blank=True
    )
    
    # Paystack recipient code (if using Paystack transfers)
    paystack_recipient_code = models.CharField(max_length=100, blank=True, null=True)
    paystack_recipient_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.restaurant.name} - Payment Profile"
    
    class Meta:
        verbose_name = "Restaurant Payment Profile"
        verbose_name_plural = "Restaurant Payment Profiles"


class RestaurantPayout(models.Model):
    """Track restaurant payouts for delivered orders"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='payouts'
    )
    
    # Payout details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Associated orders
    orders = models.ManyToManyField(
        'orders.Order', 
        related_name='payouts',
        blank=True
    )
    
    # Transaction details
    reference = models.CharField(max_length=100, unique=True)
    transfer_code = models.CharField(max_length=100, blank=True, null=True)
    paystack_transfer_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payout {self.reference} - {self.restaurant.name}"
    
    class Meta:
        verbose_name = "Restaurant Payout"
        verbose_name_plural = "Restaurant Payouts"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"PAYOUT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class RestaurantEarning(models.Model):
    """Track restaurant earnings from orders"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.CASCADE, 
        related_name='earnings'
    )
    order = models.OneToOneField(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='restaurant_earning'
    )
    
    # Financial details
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.15)  # 15% commission
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    restaurant_earning = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    is_paid_out = models.BooleanField(default=False)
    payout = models.ForeignKey(
        RestaurantPayout, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='earnings'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_out_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Earning from Order #{self.order.id} - {self.restaurant.name}"
    
    class Meta:
        verbose_name = "Restaurant Earning"
        verbose_name_plural = "Restaurant Earnings"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Calculate commission and earnings
        self.commission_amount = self.order_amount * self.commission_rate
        self.restaurant_earning = self.order_amount - self.commission_amount
        super().save(*args, **kwargs)
