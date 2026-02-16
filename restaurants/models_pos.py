from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

from .models import Restaurant
from meals.models import Meal


class POSSession(models.Model):
    """Track POS sessions/shifts for restaurants"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='pos_sessions')
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Session timing
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Financial tracking
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cash_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mpesa_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Session status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-opened_at']
        verbose_name = "POS Session"
        verbose_name_plural = "POS Sessions"
    
    def __str__(self):
        return f"POS Session - {self.restaurant.name} ({self.opened_at.date()})"
    
    @property
    def total_sales(self):
        return self.cash_sales + self.card_sales + self.mpesa_sales
    
    @property
    def order_count(self):
        return self.pos_orders.count()
    
    def close_session(self, closing_balance=None):
        """Close the POS session"""
        self.closed_at = timezone.now()
        self.is_active = False
        if closing_balance is not None:
            self.closing_balance = closing_balance
        self.save()


class POSOrder(models.Model):
    """POS orders separate from online orders"""
    
    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mpesa', 'M-Pesa'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(POSSession, on_delete=models.CASCADE, related_name='pos_orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='pos_orders')
    
    # Customer information (optional)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=15, blank=True)
    
    # Order details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    receipt_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "POS Order"
        verbose_name_plural = "POS Orders"
    
    def __str__(self):
        return f"POS Order {str(self.id)[:8]} - {self.restaurant.name}"
    
    @property
    def order_number(self):
        return str(self.id)[:8].upper()
    
    def complete_order(self):
        """Mark order as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel_order(self):
        """Cancel the order"""
        self.status = 'cancelled'
        self.save()


class POSOrderItem(models.Model):
    """Items within POS orders"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(POSOrder, on_delete=models.CASCADE, related_name='items')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    
    # Item details
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "POS Order Item"
        verbose_name_plural = "POS Order Items"
    
    def __str__(self):
        return f"{self.quantity}x {self.meal.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        # Set price to current meal price if not specified
        if not self.price:
            self.price = self.meal.price
        super().save(*args, **kwargs)


class POSReceipt(models.Model):
    """Store receipt templates and logs"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(POSOrder, on_delete=models.CASCADE, related_name='receipt')
    
    # Receipt details
    receipt_number = models.CharField(max_length=20, unique=True)
    receipt_data = models.JSONField(default=dict)  # Store receipt content
    printed_at = models.DateTimeField(null=True, blank=True)
    emailed_at = models.DateTimeField(null=True, blank=True)
    
    # Customer info for receipt
    customer_name = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "POS Receipt"
        verbose_name_plural = "POS Receipts"
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # Generate receipt number if not exists
        if not self.receipt_number:
            # Generate unique receipt number
            last_receipt = POSReceipt.objects.filter(
                order__restaurant=self.order.restaurant
            ).order_by('-created_at').first()
            
            if last_receipt:
                last_num = int(last_receipt.receipt_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.receipt_number = f"RCP-{self.order.restaurant.id:04d}-{new_num:06d}"
        
        super().save(*args, **kwargs)
