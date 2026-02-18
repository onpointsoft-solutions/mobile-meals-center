# Backend Rider System - MobileMealsCenter

## 🎯 Overview
The backend rider system provides complete rider management, order assignment, and delivery tracking functionality for the MobileMealsCenter platform.

## 📁 App Structure

### Riders App (`riders/`)
```
riders/
├── __init__.py                 # App configuration
├── apps.py                     # AppConfig
├── models.py                   # Rider models
├── admin.py                    # Admin interface
├── views.py                    # API views
├── urls.py                     # URL patterns
├── signals.py                  # Django signals
└── templates/
    └── riders/
        └── emails/
            ├── new_rider_notification.html
            └── new_assignment_notification.html
```

## 🗄️ Database Models

### 1. User Model (Extended)
Located in `accounts/models.py`

```python
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant'),
        ('rider', 'Rider'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Rider approval fields
    is_approved = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('suspended', 'Suspended')
        ],
        default='pending'
    )
```

### 2. RiderProfile Model
```python
class RiderProfile(models.Model):
    VEHICLE_TYPES = (
        ('bicycle', 'Bicycle'),
        ('motorcycle', 'Motorcycle'),
        ('car', 'Car'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Personal Information
    id_number = models.CharField(max_length=50)
    id_document = models.FileField(upload_to='riders/documents/')
    
    # Vehicle Information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    vehicle_number = models.CharField(max_length=20)
    vehicle_document = models.FileField(upload_to='riders/documents/')
    
    # Contact Information
    emergency_contact = models.CharField(max_length=20)
    
    # Banking Information
    bank_account = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    
    # Delivery Information
    delivery_areas = models.JSONField(default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_deliveries = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
```

### 3. DeliveryAssignment Model
```python
class DeliveryAssignment(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    rider = models.ForeignKey(RiderProfile, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Location tracking
    pickup_location = models.JSONField(null=True, blank=True)
    delivery_location = models.JSONField(null=True, blank=True)
```

## 🔧 Admin Interface

### RiderProfileAdmin
- **List Display**: User, approval status, vehicle type, rating, deliveries, online status
- **Filters**: Approval status, vehicle type, online status, active status
- **Search**: Username, name, vehicle number, ID number
- **Actions**: Approve riders, reject riders, suspend riders, activate riders

### DeliveryAssignmentAdmin
- **List Display**: Order, rider, status, delivery fee, timestamps
- **Filters**: Status, assigned/picked up/delivered dates
- **Actions**: Mark picked up, mark delivered, cancel assignments

### CustomUserAdmin
- Extended to show rider profile link for rider users
- Links directly to rider profile management

## 🌐 API Endpoints

### Authentication
```
POST /api/riders/login/                    # Rider login with approval check
```

### Profile Management
```
GET  /api/riders/profile/                  # Get current rider profile
POST /api/riders/profile/create/           # Create/update rider profile
POST /api/riders/toggle-online/            # Toggle online status
```

### Order Management
```
GET  /api/riders/available-orders/         # Get available orders for pickup
GET  /api/riders/active-orders/            # Get active delivery assignments
POST /api/riders/accept-order/<id>/        # Accept a delivery order
PUT  /api/riders/update-delivery/<id>/     # Update delivery status
```

### Analytics
```
GET  /api/riders/earnings/                 # Get rider earnings data
GET  /api/riders/delivery-history/         # Get complete delivery history
```

## 🔄 Django Signals

### User Creation Signal
- Automatically creates RiderProfile when rider user is created
- Sends admin notification for new rider registration

### Delivery Assignment Signals
- Updates order status when assignment is created
- Sends rider notification for new assignments
- Updates rider statistics when delivery is completed
- Sends customer notification when order is delivered

### Status Change Signals
- Handles order status transitions
- Sends appropriate notifications
- Updates performance metrics

## 📧 Email Notifications

### New Rider Registration
- Sent to admin when new rider registers
- Includes rider details and approval link
- Template: `riders/emails/new_rider_notification.html`

### New Delivery Assignment
- Sent to rider when assigned to delivery
- Includes order details and pickup information
- Template: `riders/emails/new_assignment_notification.html`

### Order Delivered
- Sent to customer when order is delivered
- Includes rider information and delivery details

## 🔒 Security Features

### Authentication
- Custom rider login with approval validation
- Token-based authentication for API access
- Session management with timeout

### Approval System
- Admin approval required for rider activation
- Status tracking: pending → approved → active
- Suspension capability for policy violations

### Data Protection
- Document upload validation
- Secure file storage
- Input sanitization and validation

## 📊 Business Logic

### Order Assignment Flow
1. Customer places order → Order status: `ready`
2. System notifies approved/online riders
3. Rider accepts order → Create DeliveryAssignment
4. Order status: `delivering`
5. Rider picks up order → Assignment status: `picked_up`
6. Rider delivers order → Assignment status: `delivered`
7. Order status: `delivered`
8. Update rider statistics and earnings

### Online Status Management
- Riders can toggle online status via API
- Only online riders receive order notifications
- Automatic offline after inactivity

### Performance Tracking
- Rating system based on customer feedback
- Delivery completion statistics
- Earnings calculation and tracking

## 🚀 Configuration

### Settings Configuration
```python
# Add to INSTALLED_APPS
'riders',

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Email configuration for notifications
DEFAULT_FROM_EMAIL = 'Mobile Meals Center <noreply@mobilemealscenter.com>'
ADMINS = [('Admin', 'admin@mobilemealscenter.co.ke')]
```

### URL Configuration
```python
# Add to main urls.py
path('api/riders/', include('riders.urls')),
```

## 📱 Mobile App Integration

### Authentication Flow
1. Rider registers → Creates User + RiderProfile (pending)
2. Admin approves → User.approval_status = 'approved'
3. Rider logs in → Validates approval status
4. Access granted to rider features

### Real-time Features
- Order notifications via API polling
- Status updates in real-time
- Location tracking (extendable)

### Data Synchronization
- Profile updates sync immediately
- Order status updates propagate
- Earnings calculations in real-time

## 🧪 Testing

### Model Tests
- RiderProfile creation and validation
- DeliveryAssignment lifecycle
- User approval workflow

### API Tests
- Authentication endpoints
- Profile management
- Order assignment flow
- Status updates

### Integration Tests
- End-to-end order delivery
- Email notifications
- Admin approval workflow

## 📈 Performance Optimizations

### Database
- Optimized queries with select_related/prefetch_related
- Indexes on frequently queried fields
- Efficient status tracking

### API Performance
- Pagination for large datasets
- Caching for frequently accessed data
- Optimized response structures

### File Storage
- Efficient document upload handling
- Image compression for profile photos
- Cloud storage integration ready

## 🔧 Maintenance

### Database Migrations
```bash
python manage.py makemigrations riders
python manage.py migrate
```

### Admin Setup
- Create superuser for admin access
- Configure rider approval workflow
- Set up email notifications

### Monitoring
- Rider activity tracking
- Order completion metrics
- System performance monitoring

## 🎯 Key Features Implemented

✅ **Complete Rider Management**
- User registration with profile creation
- Admin approval workflow
- Document upload and verification

✅ **Order Assignment System**
- Real-time order notifications
- Efficient assignment algorithm
- Status tracking and updates

✅ **Delivery Tracking**
- Complete delivery lifecycle
- Location tracking ready
- Customer notifications

✅ **Performance Analytics**
- Rider rating system
- Earnings calculation
- Delivery statistics

✅ **Admin Interface**
- Comprehensive rider management
- Order assignment oversight
- Performance monitoring

✅ **API Integration**
- RESTful API endpoints
- Mobile app ready
- Real-time updates

The backend rider system is now fully implemented and ready for production use with the MobileMealsCenter mobile app! 🚀
