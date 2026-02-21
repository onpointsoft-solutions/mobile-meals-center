# Africa's Talking SMS Integration Setup

## Overview
This guide will help you set up Africa's Talking SMS gateway for Mobile Meals Center to send automated SMS notifications to customers and riders.

## Prerequisites
- Africa's Talking account (sign up at https://account.africastalking.com/)
- Python environment with Django installed
- Mobile Meals Center project setup

## Step 1: Get Africa's Talking Credentials

1. **Sign up for Africa's Talking account**
   - Go to https://account.africastalking.com/
   - Create an account or log in
   - Verify your email and phone number

2. **Get your API credentials**
   - Navigate to the Dashboard
   - Go to "API" section
   - Note down your:
     - **Username** (usually your account username)
     - **API Key** (click "Show API Key" to reveal)

3. **Choose your environment**
   - **Sandbox**: Free for testing, messages are not actually sent
   - **Production**: Paid service, actual SMS delivery

## Step 2: Configure Environment Variables

1. **Copy the example environment file**
   ```bash
   cp .env.example .env
   ```

2. **Edit your .env file**
   ```env
   # Africa's Talking SMS Configuration
   AFRICASTALKING_USERNAME=sandbox  # Use 'sandbox' for testing, your username for production
   AFRICASTALKING_API_KEY=your_api_key_here
   AFRICASTALKING_SENDER_ID=MobileMeals
   
   # SMS Configuration
   SMS_ENABLED=True
   SMS_DEBUG=False
   ```

3. **For production use**
   ```env
   AFRICASTALKING_USERNAME=your_actual_username
   AFRICASTALKING_API_KEY=your_production_api_key
   AFRICASTALKING_SENDER_ID=MobileMeals
   ```

## Step 3: Install Dependencies

The required package is already installed, but if needed:
```bash
pip install africastalking
```

## Step 4: Test the Integration

### Method 1: Using Management Command
```bash
python manage.py send_test_sms --phone "+254712345678" --message "Test SMS from Mobile Meals Center"
```

### Method 2: Using SMS Dashboard
1. Access your admin panel
2. Navigate to SMS Dashboard
3. Enter a test phone number
4. Click "Send Test SMS"

## Step 5: Verify Phone Numbers

Ensure users have valid phone numbers in their profiles:
- **Customers**: Check in User Management
- **Riders**: Check in Rider Management
- **Format**: International format (+254712345678)

## Automated SMS Notifications

The system automatically sends SMS for these events:

### 1. Order Confirmation
- **When**: Customer places an order
- **To**: Customer
- **Content**: Order details, restaurant info, total amount

### 2. Rider Assignment
- **When**: Admin assigns order to rider
- **To**: Rider
- **Content**: Assignment details, pickup location, customer info

### 3. Customer Rider Notification
- **When**: Rider is assigned to order
- **To**: Customer
- **Content**: Rider details, estimated delivery time

### 4. Order Delivery
- **When**: Order is marked as delivered
- **To**: Customer
- **Content**: Delivery confirmation, rating request

## SMS Templates

### Order Confirmation
```
Dear [Customer Name],

Your order #[Order Number] has been confirmed!

Order Details:
• Restaurant: [Restaurant Name]
• Amount: KES [Total Amount]
• Delivery Address: [Delivery Address]

We'll notify you when a rider is assigned.

Thank you for choosing Mobile Meals Center!
📱 +254712345678
```

### Rider Assignment
```
Hello [Rider Name],

New delivery assignment!

Order Details:
• Order #: [Order Number]
• Restaurant: [Restaurant Name]
• Customer: [Customer Name]
• Delivery Address: [Delivery Address]
• Customer Phone: [Customer Phone]
• Delivery Fee: KES [Delivery Fee]

Please accept and proceed to pickup.

Thank you!
Mobile Meals Center
```

## Troubleshooting

### Common Issues

1. **"SMS service is not active"**
   - Check your Africa's Talking credentials
   - Verify API key is correct
   - Ensure username is correct

2. **"Invalid phone number format"**
   - Use international format: +254712345678
   - Include country code
   - No spaces or special characters

3. **"No valid phone numbers provided"**
   - Check user profiles have phone numbers
   - Verify phone number format in database

4. **API Key Issues**
   - Regenerate API key from Africa's Talking dashboard
   - Ensure API key is not expired
   - Check if account is active

### Debug Mode

Enable debug mode for detailed logging:
```env
SMS_DEBUG=True
```

Check Django logs for detailed error messages.

## Production Considerations

1. **SMS Costs**
   - Monitor SMS usage in Africa's Talking dashboard
   - Set up payment method for production use
   - Consider SMS volume and costs

2. **Rate Limits**
   - Africa's Talking has rate limits
   - Implement queue system for bulk SMS
   - Handle failed deliveries gracefully

3. **Compliance**
   - Ensure compliance with local SMS regulations
   - Include opt-out options if required
   - Maintain SMS logs for audit purposes

## Monitoring and Analytics

1. **SMS Dashboard**
   - View service status
   - Send test SMS
   - Monitor configuration

2. **Logs**
   - Check Django logs for SMS activities
   - Monitor failed deliveries
   - Track SMS costs

3. **Africa's Talking Dashboard**
   - Monitor SMS usage
   - View delivery reports
   - Manage account settings

## Support

For Africa's Talking specific issues:
- Email: support@africastalking.com
- Documentation: https://developers.africastalking.com/
- Live chat available on their website

For Mobile Meals Center SMS integration:
- Check Django logs
- Verify configuration
- Test with management command

## Security Notes

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate API keys regularly

2. **Phone Number Privacy**
   - Secure phone number data
   - Implement access controls
   - Follow data protection regulations

3. **SMS Content**
   - Avoid sensitive information in SMS
   - Use secure channels for sensitive data
   - Implement content filtering if needed
