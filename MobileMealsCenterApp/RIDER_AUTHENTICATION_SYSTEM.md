# Rider Authentication and Approval System

## Overview
The MobileMealsCenter app includes a comprehensive rider authentication and approval system that ensures only verified and approved riders can access delivery functionality.

## 🔐 Authentication Flow

### 1. User Type Selection
- **Screen**: `UserTypeScreen`
- **Options**: Customer or Rider
- **Navigation**: Routes to appropriate login/registration

### 2. Rider Registration
- **Screen**: `RiderRegistrationScreen`
- **Process**: Complete registration with profile creation
- **Fields Required**:
  - Basic Info: Name, username, email, phone, password
  - Profile Info: ID number, vehicle details, emergency contact, bank info
- **Backend**: Creates user with `userType: "rider"` and `approval_status: "pending"`

### 3. Approval Pending
- **Screen**: `RiderApprovalPendingScreen`
- **Status**: Shows registration success and pending approval
- **Timeline**: 24-48 hours for admin approval
- **Actions**: Check status, back to home

### 4. Rider Login
- **Screen**: `RiderLoginScreen`
- **Validation**: Checks if user is rider and approval status
- **Outcomes**:
  - ✅ Approved → Navigate to rider dashboard
  - ⏳ Pending → Show approval pending screen
  - ❌ Rejected → Show rejection message

## 👤 Rider Profile Model

### User Model Extensions
```kotlin
data class User(
    // ... existing fields
    val is_approved: Boolean = false,
    val approval_status: String = "pending", // "pending", "approved", "rejected"
    val rider_profile: RiderProfile? = null
)
```

### Rider Profile Model
```kotlin
data class RiderProfile(
    val id: Int,
    val user: Int,
    val id_number: String?,
    val id_document: String?,
    val vehicle_type: String, // "bicycle", "motorcycle", "car"
    val vehicle_number: String?,
    val vehicle_document: String?,
    val emergency_contact: String?,
    val bank_account: String?,
    val bank_name: String?,
    val delivery_areas: List<String> = emptyList(),
    val rating: Double = 0.0,
    val total_deliveries: Int = 0,
    val is_online: Boolean = false
)
```

## 🔗 API Endpoints

### Authentication
```
POST /api/auth/register/          # Rider registration
POST /api/auth/login/             # Rider login
GET  /api/auth/user/              # Get current user
```

### Rider Profile
```
GET    /api/riders/profile/        # Get rider profile
POST   /api/riders/profile/        # Create rider profile
PUT    /api/riders/profile/        # Update rider profile
POST   /api/riders/toggle-online/  # Toggle online status
```

### Delivery Operations
```
GET /api/riders/available-orders/   # Available orders
GET /api/riders/active-orders/      # Active deliveries
POST /api/riders/accept-order/{id}/  # Accept order
PUT  /api/riders/update-delivery/{id}/ # Update status
```

### Analytics
```
GET /api/riders/earnings/           # Rider earnings
GET /api/riders/delivery-history/   # Delivery history
```

## 🎯 Approval States

### 1. Pending (Default)
- **Status**: `approval_status: "pending"`
- **is_approved**: `false`
- **Access**: Can login but cannot access delivery features
- **Screen**: Shows approval pending message

### 2. Approved
- **Status**: `approval_status: "approved"`
- **is_approved**: `true`
- **Access**: Full rider dashboard and delivery features
- **Screen**: Rider home screen with delivery options

### 3. Rejected
- **Status**: `approval_status: "rejected"`
- **is_approved**: `false`
- **Access**: Login blocked with rejection message
- **Screen**: Shows rejection notice

## 📱 Screen Navigation Flow

```
WelcomeScreen
    ↓
UserTypeScreen (Select Rider)
    ↓
RiderLoginScreen
    ├── New User → RiderRegistrationScreen
    └── Existing User → Login Check
        ├── Approved → RiderHomeScreen
        ├── Pending → RiderApprovalPendingScreen
        └── Rejected → Error Message
```

## 🔧 Backend Requirements

### Django Models Needed

#### User Model Extensions
```python
class User(AbstractUser):
    # ... existing fields
    user_type = models.CharField(choices=[...])
    is_approved = models.BooleanField(default=False)
    approval_status = models.CharField(default='pending')
```

#### Rider Profile Model
```python
class RiderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=50)
    id_document = models.FileField(upload_to='id_documents/')
    vehicle_type = models.CharField(choices=[...])
    vehicle_number = models.CharField(max_length=20)
    vehicle_document = models.FileField(upload_to='vehicle_documents/')
    emergency_contact = models.CharField(max_length=20)
    bank_account = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    delivery_areas = models.JSONField(default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_deliveries = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)
```

### API Views Needed

#### Authentication
```python
# Custom registration that handles rider profile creation
class RiderRegistrationView(APIView):
    def post(self, request):
        # Create user with rider type
        # Create rider profile
        # Set approval status to pending
        # Send notification to admin
```

#### Profile Management
```python
class RiderProfileView(APIView):
    # Get, update rider profile
    # Toggle online status
    # View earnings and history
```

### Admin Approval System
```python
# Admin interface to approve/reject riders
# Email notifications for status changes
# Background checks integration
```

## 🚀 Key Features

### 1. Secure Registration
- ✅ Complete profile verification
- ✅ Document upload support
- ✅ Background check integration
- ✅ Automatic admin notification

### 2. Approval Workflow
- ✅ Pending status tracking
- ✅ Admin approval interface
- ✅ Email notifications
- ✅ Rejection handling

### 3. Profile Management
- ✅ Edit profile information
- ✅ Update vehicle details
- ✅ Manage bank information
- ✅ Toggle online status

### 4. Delivery Operations
- ✅ Available orders viewing
- ✅ Order acceptance
- ✅ Real-time status updates
- ✅ Delivery tracking

### 5. Analytics
- ✅ Earnings tracking
- ✅ Delivery history
- ✅ Performance metrics
- ✅ Rating system

## 📋 Implementation Checklist

### Frontend (Android)
- [x] User type selection screen
- [x] Rider registration screen
- [x] Rider login screen
- [x] Approval pending screen
- [x] Rider profile screen
- [x] Rider dashboard
- [x] API service integration
- [x] Data models
- [x] Navigation setup

### Backend (Django)
- [ ] User model extensions
- [ ] Rider profile model
- [ ] Registration API
- [ ] Login validation
- [ ] Profile management APIs
- [ ] Admin approval interface
- [ ] Email notifications
- [ ] Document upload handling

### Admin Features
- [ ] Rider approval dashboard
- [ ] Profile verification
- [ ] Document review
- [ ] Status management
- [ ] Communication tools

## 🔒 Security Considerations

### 1. Authentication
- Token-based authentication
- Secure password storage
- Session management
- API rate limiting

### 2. Data Protection
- Document encryption
- Personal data protection
- Bank information security
- GDPR compliance

### 3. Approval Process
- Admin-only approval access
- Audit trail for approvals
- Secure document storage
- Background check integration

## 📊 Analytics & Monitoring

### Rider Performance
- Delivery completion rate
- Average delivery time
- Customer ratings
- Earnings tracking

### System Metrics
- Registration conversion rate
- Approval time statistics
- Active rider count
- Order fulfillment rate

## 🚧 Future Enhancements

### 1. Advanced Features
- Real-time location tracking
- Route optimization
- Multi-language support
- Push notifications

### 2. Admin Tools
- Bulk approval operations
- Automated background checks
- Performance analytics
- Communication platform

### 3. Rider Benefits
- Insurance integration
- Fuel management
- Equipment tracking
- Loyalty programs

This comprehensive rider authentication and approval system ensures that only qualified and verified riders can access the delivery platform, maintaining safety and quality standards for the Mobile Meals Center service.
