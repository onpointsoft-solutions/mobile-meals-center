"""
Test script to verify email configuration
Run this with: python manage.py shell < test_email.py
"""

from django.core.mail import send_mail
from django.conf import settings

print("Testing email configuration...")
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")

try:
    send_mail(
        subject='Test Email - Mobile Meals Center',
        message='This is a test email to verify the email configuration is working correctly.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['test@example.com'],
        fail_silently=False,
    )
    print("✅ Test email sent successfully!")
    print("Check your console for the email output (using console backend)")
except Exception as e:
    print(f"❌ Error sending test email: {str(e)}")
