from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from superadmin.models import SystemSettings
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize system settings for delivery fee and commission'

    def handle(self, *args, **options):
        # Default settings
        default_settings = {
            'delivery_fee': '50.00',
            'commission_rate': '10.00',  # 10% commission
            'tax_rate': '8.00',  # 8% tax
        }
        
        descriptions = {
            'delivery_fee': 'Delivery fee charged to customers for online orders',
            'commission_rate': 'Commission percentage charged to restaurants (percentage)',
            'tax_rate': 'Tax rate applied to orders (percentage)',
        }
        
        for key, value in default_settings.items():
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': descriptions.get(key, ''),
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created setting: {key} = {value}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Setting already exists: {key} = {setting.value}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('System settings initialized successfully!')
        )
