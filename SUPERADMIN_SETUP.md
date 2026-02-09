# Super Admin Setup Guide

## Overview

The Super Admin system provides a comprehensive dashboard for managing your Mobile Meals Center platform. It includes:

- **Dashboard**: Overview with statistics and analytics
- **Restaurant Management**: View, activate/suspend restaurants
- **User Management**: Manage customers, restaurant owners, and admins
- **Order Monitoring**: Track all orders across the platform
- **Category Management**: View meal categories
- **Activity Log**: Track all admin actions
- **System Settings**: Configure platform-wide settings

---

## Installation Steps

### 1. Run Migrations

After adding the superadmin app, create and run migrations:

```bash
python manage.py makemigrations superadmin
python manage.py migrate
```

This will create the following database tables:
- `superadmin_systemsettings` - Store system configuration
- `superadmin_adminactivitylog` - Track admin actions

### 2. Create a Superuser

If you don't already have a superuser account:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 3. Access the Super Admin Panel

Navigate to: `https://yourdomain.com/superadmin/`

You must be logged in as a superuser to access this area.

---

## Features

### 📊 Dashboard (`/superadmin/`)

**Statistics Overview:**
- Total users, restaurants, orders, and revenue
- Weekly growth metrics
- Order status breakdown with progress bars
- Top performing restaurants
- Recent orders and new users
- Admin activity log

### 🏪 Restaurant Management (`/superadmin/restaurants/`)

**Features:**
- View all restaurants with owner details
- See meal count, order count, and revenue per restaurant
- Search and filter by status (active/inactive)
- Activate or suspend restaurants
- View detailed restaurant information

**Actions:**
- Click eye icon to view restaurant details
- Click toggle button to activate/suspend
- All actions are logged

### 👥 User Management (`/superadmin/users/`)

**Features:**
- View all users (customers, restaurant owners, admins)
- Search by username, email, or name
- Filter by user type and status
- Activate or suspend user accounts
- Protected superuser accounts cannot be modified

**User Types:**
- **Admin** (red badge) - Superusers
- **Restaurant** (green badge) - Restaurant owners
- **Customer** (blue badge) - Regular customers

### 📦 Order Management (`/superadmin/orders/`)

**Features:**
- Monitor all orders across the platform
- Search by order number, customer, or restaurant
- Filter by order status
- View order details including customer and restaurant info
- Track order amounts and timestamps

**Order Statuses:**
- Pending (yellow)
- Confirmed (blue)
- Preparing (blue)
- Ready (green)
- Delivered (green)
- Cancelled (red)

### 🏷️ Category Management (`/superadmin/categories/`)

**Features:**
- View all meal categories
- See meal count per category
- Categories can be managed via Django admin panel

### 📝 Activity Log (`/superadmin/activity_log/`)

**Tracks:**
- Admin username
- Action type (create, update, delete, approve, reject, suspend, activate)
- Target model and ID
- Description of action
- Timestamp and IP address

**Use Cases:**
- Audit trail for compliance
- Track who made changes
- Investigate issues
- Monitor admin activity

### ⚙️ System Settings (`/superadmin/settings/`)

**Features:**
- View system-wide configuration
- Settings managed via Django admin panel
- Track who updated settings and when

---

## Permissions

### Access Control

The super admin panel uses `SuperAdminRequiredMixin` which:
- Requires user to be authenticated
- Requires user to have `is_superuser=True`
- Redirects unauthorized users to home page with error message

### Protected Actions

- Superuser accounts cannot be suspended
- All actions are logged with admin username and IP address
- Confirmation dialogs for destructive actions

---

## Activity Logging

All admin actions are automatically logged to the `AdminActivityLog` model:

```python
AdminActivityLog.objects.create(
    admin=request.user,
    action='suspend',  # or 'activate', 'update', etc.
    target_model='Restaurant',
    target_id=restaurant.id,
    description='Suspended restaurant: Pizza Palace',
    ip_address=request.META.get('REMOTE_ADDR')
)
```

---

## Customization

### Adding New Settings

Add settings via Django admin or programmatically:

```python
from superadmin.models import SystemSettings

SystemSettings.objects.create(
    key='max_orders_per_day',
    value='100',
    description='Maximum orders allowed per day',
    updated_by=request.user
)
```

### Extending the Dashboard

To add more statistics to the dashboard, edit `superadmin/views.py`:

```python
class AdminDashboardView(SuperAdminRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your custom statistics here
        context['custom_stat'] = YourModel.objects.count()
        return context
```

---

## Security Best Practices

1. **Limit Superuser Access**: Only create superuser accounts for trusted administrators
2. **Monitor Activity Logs**: Regularly review admin actions
3. **Use Strong Passwords**: Enforce strong password policies for admin accounts
4. **Enable 2FA**: Consider adding two-factor authentication (future enhancement)
5. **Restrict IP Access**: Use firewall rules to limit admin panel access
6. **Regular Audits**: Review user permissions and access logs monthly

---

## Troubleshooting

### Cannot Access Super Admin Panel

**Error**: "You do not have permission to access this page"

**Solution**: Ensure your user account has `is_superuser=True`:

```bash
python manage.py shell
```

```python
from accounts.models import User
user = User.objects.get(username='yourusername')
user.is_superuser = True
user.is_staff = True
user.save()
```

### Missing Statistics

**Issue**: Dashboard shows zero for all statistics

**Solution**: Ensure you have data in the database:
- Create some test restaurants
- Place some test orders
- Register some users

### Activity Log Not Recording

**Issue**: Actions not appearing in activity log

**Solution**: Check that views are calling `AdminActivityLog.objects.create()` after actions

---

## URLs Reference

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/superadmin/` | Main admin dashboard |
| Restaurants | `/superadmin/restaurants/` | Restaurant management |
| Restaurant Detail | `/superadmin/restaurants/<id>/` | View restaurant details |
| Users | `/superadmin/users/` | User management |
| Orders | `/superadmin/orders/` | Order monitoring |
| Categories | `/superadmin/categories/` | Category list |
| Activity Log | `/superadmin/activity-log/` | Admin action history |
| Settings | `/superadmin/settings/` | System settings |

---

## Mobile Responsiveness

The super admin panel is fully responsive:
- Sidebar collapses on mobile devices
- Tables scroll horizontally on small screens
- Touch-friendly buttons and controls
- Mobile menu toggle button

---

## Future Enhancements

Potential features to add:
- [ ] Export data to CSV/Excel
- [ ] Advanced analytics and charts
- [ ] Email notifications for critical events
- [ ] Two-factor authentication
- [ ] Bulk actions (suspend multiple restaurants)
- [ ] Custom report generation
- [ ] Real-time dashboard updates
- [ ] Role-based permissions (staff vs superuser)

---

## Support

For issues or questions:
1. Check the activity log for error details
2. Review Django error logs
3. Ensure all migrations are applied
4. Verify user permissions

---

*Mobile Meals Center - Super Admin Panel* 🔐
