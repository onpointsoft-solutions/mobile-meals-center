from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['key']
    
    def __str__(self):
        return self.key


class AdminActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('suspend', 'Suspend'),
        ('activate', 'Activate'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=36)  # Can store both integers and UUIDs
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Admin Activity Log'
        verbose_name_plural = 'Admin Activity Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.target_model} #{self.target_id}"


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('order', 'Order Issue'),
        ('restaurant', 'Restaurant Issue'),
        ('payment', 'Payment Issue'),
        ('delivery', 'Delivery Issue'),
        ('quality', 'Food Quality'),
        ('service', 'Customer Service'),
        ('technical', 'Technical Issue'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    order_number = models.CharField(max_length=50, blank=True, null=True, help_text='Related order number if applicable')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    admin_notes = models.TextField(blank=True, help_text='Internal notes from admin')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_complaints')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.get_status_display()})"
    
    def mark_resolved(self, admin_user):
        self.status = 'resolved'
        self.resolved_by = admin_user
        self.resolved_at = timezone.now()
        self.save()
