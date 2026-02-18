from django.core.cache import cache
from superadmin.models import SystemSettings
from decimal import Decimal

def get_system_setting(key, default=None):
    """Get a system setting value with caching"""
    cache_key = f'system_setting_{key}'
    cached_value = cache.get(cache_key)
    
    if cached_value is not None:
        return cached_value
    
    try:
        setting = SystemSettings.objects.get(key=key)
        value = setting.value
        
        # Cache for 1 hour
        cache.set(cache_key, value, 3600)
        
        return value
    except SystemSettings.DoesNotExist:
        return default

def get_delivery_fee():
    """Get delivery fee from system settings"""
    fee = get_system_setting('delivery_fee', '50.00')
    try:
        return Decimal(fee)
    except:
        return Decimal('50.00')

def get_commission_rate():
    """Get commission rate from system settings"""
    rate = get_system_setting('commission_rate', '10.00')
    try:
        return Decimal(rate)
    except:
        return Decimal('10.00')

def get_tax_rate():
    """Get tax rate from system settings"""
    rate = get_system_setting('tax_rate', '8.00')
    try:
        return Decimal(rate)
    except:
        return Decimal('8.00')

def clear_system_settings_cache():
    """Clear all system settings cache"""
    cache.delete_many([
        'system_setting_delivery_fee',
        'system_setting_commission_rate',
        'system_setting_tax_rate',
    ])
