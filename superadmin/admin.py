from django.contrib import admin
from .models import SystemSettings, AdminActivityLog, Complaint


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at', 'updated_by']
    search_fields = ['key', 'value', 'description']
    list_filter = ['updated_at']
    readonly_fields = ['updated_at']


@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = ['admin', 'action', 'target_model', 'target_id', 'created_at']
    list_filter = ['action', 'target_model', 'created_at']
    search_fields = ['admin__username', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['status', 'category', 'priority', 'created_at']
    search_fields = ['user__username', 'subject', 'description', 'order_number']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Complaint Information', {
            'fields': ('user', 'category', 'subject', 'description', 'order_number')
        }),
        ('Status', {
            'fields': ('status', 'priority', 'admin_notes')
        }),
        ('Resolution', {
            'fields': ('resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
