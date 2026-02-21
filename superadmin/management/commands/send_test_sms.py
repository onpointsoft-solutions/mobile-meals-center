"""
Django management command to send test SMS
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sms_service import sms_service

class Command(BaseCommand):
    help = 'Send test SMS to verify Africa\'s Talking integration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to send test SMS to (in international format, e.g., +254712345678)'
        )
        parser.add_argument(
            '--message',
            type=str,
            default='Test SMS from Mobile Meals Center - Africa\'s Talking integration working! 🎉',
            help='Custom test message'
        )
    
    def handle(self, *args, **options):
        phone = options.get('phone')
        message = options.get('message')
        
        if not phone:
            self.stdout.write(self.style.ERROR('Please provide a phone number with --phone'))
            return
        
        self.stdout.write(f"Sending test SMS to {phone}...")
        self.stdout.write(f"Message: {message}")
        
        # Check SMS service status
        if not sms_service.is_active:
            self.stdout.write(self.style.ERROR('SMS service is not active. Check your credentials.'))
            return
        
        # Send test SMS
        response = sms_service.send_sms(phone, message)
        
        if response['status'] == 'success':
            self.stdout.write(self.style.SUCCESS('✅ Test SMS sent successfully!'))
            self.stdout.write(f"Response: {response}")
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send test SMS'))
            self.stdout.write(f"Error: {response['message']}")
            
        # Show configuration info
        self.stdout.write("\n" + "="*50)
        self.stdout.write("SMS Configuration:")
        self.stdout.write(f"Username: {settings.AFRICASTALKING_USERNAME}")
        self.stdout.write(f"API Key: {'*' * len(settings.AFRICASTALKING_API_KEY) if settings.AFRICASTALKING_API_KEY else 'Not set'}")
        self.stdout.write(f"Sender ID: {settings.AFRICASTALKING_SENDER_ID}")
        self.stdout.write(f"SMS Enabled: {getattr(settings, 'SMS_ENABLED', False)}")
        self.stdout.write("="*50)
