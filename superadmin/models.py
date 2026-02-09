from django.db import models
from django.contrib.auth import get_user_model

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
    target_id = models.IntegerField()
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Admin Activity Log'
        verbose_name_plural = 'Admin Activity Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.target_model} #{self.target_id}"
