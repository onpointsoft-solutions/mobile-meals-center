# Email Configuration Guide - Mobile Meals Center

## Current Setup

The system is configured to send emails for order confirmations and restaurant notifications.

### Email Backend

**Development Mode (Current):**
- Backend: `django.core.mail.backends.console.EmailBackend`
- Emails are printed to the console/terminal where the Django server is running
- No actual emails are sent (perfect for testing)

**Production Mode (To Enable Later):**
Edit `config/settings.py` and uncomment the SMTP settings:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mobilemealscenter@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
```

### Gmail Setup (For Production)

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password:
   - Go to Security > 2-Step Verification > App passwords
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password
   - Use this in `EMAIL_HOST_PASSWORD`

## Email Types

### 1. Customer Order Confirmation
**Trigger:** When an order is placed and payment is confirmed
**Recipient:** Customer email
**Templates:**
- HTML: `templates/emails/order_confirmation.html`
- Text: `templates/emails/order_confirmation.txt`

**Content:**
- Order number and details
- Restaurant information
- Itemized order with prices (KES)
- Delivery information
- Payment method
- Tracking link

### 2. Restaurant New Order Notification
**Trigger:** When a new order is received
**Recipient:** Restaurant owner/manager email
**Templates:**
- HTML: `templates/emails/restaurant_notification.html`
- Text: `templates/emails/restaurant_notification.txt`

**Content:**
- Order alert banner
- Customer contact information
- Delivery address
- Payment method (Cash on Delivery highlighted)
- Itemized order with prices (KES)
- Action buttons to view order
- Preparation instructions

## Testing Emails

### Method 1: Using Test Script
```bash
python manage.py shell < test_email.py
```

### Method 2: Place a Test Order
1. Create a customer account
2. Add items to cart
3. Complete checkout
4. Select "Pay on Delivery"
5. Confirm order
6. Check your terminal/console for email output

### Method 3: Django Shell
```python
python manage.py shell

from core.email_utils import send_order_confirmation_email, send_restaurant_notification_email
from orders.models import Order
from payments.models import Payment

# Get a test order
order = Order.objects.first()
payment = order.payment

# Send test emails
send_order_confirmation_email(order, payment)
send_restaurant_notification_email(order, payment)
```

## Email Functions

Located in `core/email_utils.py`:

1. **`send_order_confirmation_email(order, payment)`**
   - Sends confirmation to customer
   - Returns True on success, False on failure

2. **`send_restaurant_notification_email(order, payment)`**
   - Sends notification to restaurant
   - Tries multiple email sources (restaurant.email, owner.email, user.email)
   - Returns True on success, False on failure

3. **`send_order_status_update_email(order, new_status)`**
   - Sends status updates to customer
   - Triggered when order status changes

## Payment Methods

### Current Status

✅ **Cash on Delivery** - Active and Primary
- Fully functional
- Emails sent immediately on order confirmation
- No payment gateway required

⏳ **Credit/Debit Card** - Coming Soon
- Requires Stripe configuration
- Marked as "Coming Soon" in UI

⏳ **M-Pesa** - Coming Soon
- Requires M-Pesa API integration
- Marked as "Coming Soon" in UI

## Troubleshooting

### Emails not appearing in console?
- Make sure Django development server is running
- Check that `EMAIL_BACKEND` is set to console backend
- Look for email output in the terminal where you ran `python manage.py runserver`

### Restaurant not receiving emails?
- Check that the restaurant has an email set
- Verify the restaurant owner/user has an email
- Check logs: `logger.warning` messages will show if no email found

### Email formatting issues?
- HTML emails use inline CSS for compatibility
- Text versions are provided as fallback
- Test with different email clients

## Contact Information

Default sender: `Mobile Meals Center <noreply@mobilemeals.com>`
Support email: `mobilemealscenter@gmail.com`
Support phone: `+254702502952`

## Next Steps

1. ✅ Test emails in development (console backend)
2. ⏳ Set up Gmail App Password for production
3. ⏳ Update email templates with your branding
4. ⏳ Add email field to Restaurant model (optional)
5. ⏳ Configure email notifications for order status changes
6. ⏳ Set up email templates for password reset
