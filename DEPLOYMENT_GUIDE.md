# Deployment Guide - Mobile Meals Center

## Passenger (cPanel) Deployment

This guide covers deploying the Mobile Meals Center application using Passenger WSGI on cPanel hosting.

---

## Prerequisites

- cPanel hosting account with Python support
- SSH access (recommended)
- MySQL database access
- Domain or subdomain configured

---

## Step 1: Prepare Your Server

### 1.1 Create Database

1. Log into cPanel
2. Go to **MySQL Databases**
3. Create a new database: `mobilemealscenter`
4. Create a database user: `niebzdyl_admin`
5. Set a strong password: `@Admin@20266` (or your chosen password)
6. Add user to database with **ALL PRIVILEGES**

### 1.2 Note Your Database Details

```
Database Name: mobilemealscenter
Database User: niebzdyl_admin
Database Password: @Admin@20266
Database Host: localhost
```

---

## Step 2: Upload Application Files

### Option A: Using Git (Recommended)

```bash
# SSH into your server
ssh username@yourdomain.com

# Navigate to your application directory
cd ~/public_html  # or your desired directory

# Clone the repository
git clone https://github.com/onpointsoft-solutions/mobile-meals-center.git
cd mobile-meals-center
```

### Option B: Using File Manager/FTP

1. Compress your project folder locally
2. Upload via cPanel File Manager or FTP
3. Extract in your desired directory

---

## Step 3: Set Up Python Virtual Environment

```bash
# Navigate to your project directory
cd ~/public_html/mobile-meals-center

# Create virtual environment (Python 3.11 or available version)
python3.11 -m venv env

# Activate virtual environment
source env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

---

## Step 4: Install Dependencies

```bash
# Make sure virtual environment is activated
source env/bin/activate

# Install requirements
pip install -r requirements.txt

# If mysqlclient fails, try:
pip install --only-binary :all: mysqlclient
# Or use PyMySQL as alternative
```

---

## Step 5: Configure Settings

### 5.1 Update Database Settings

The database settings are already configured in `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mobilemealscenter',
        'USER': 'niebzdyl_admin',
        'PASSWORD': '@Admin@20266',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### 5.2 Update Production Settings

Edit `config/settings.py`:

```python
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your-ip-address']

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 5.3 Update Email Settings

Ensure your email settings are correct:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mobilemealscenter@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## Step 6: Run Migrations

```bash
# Activate virtual environment
source env/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

---

## Step 7: Configure Passenger

### 7.1 Verify passenger_wsgi.py

The `passenger_wsgi.py` file is already created. Verify the Python version path:

```python
# Update this line to match your Python version
venv_path = os.path.join(project_home, 'env', 'lib', 'python3.11', 'site-packages')
```

Check your Python version:
```bash
python --version
```

### 7.2 Set Up Application in cPanel

1. Log into cPanel
2. Go to **Setup Python App** (or **Python Selector**)
3. Click **Create Application**
4. Configure:
   - **Python version**: 3.11 (or available version)
   - **Application root**: `/home/username/public_html/mobile-meals-center`
   - **Application URL**: `/` (or your subdomain)
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`

5. Click **Create**

### 7.3 Set Environment Variables (Optional)

In the Python App interface, add environment variables:
```
DJANGO_SETTINGS_MODULE=config.settings
```

---

## Step 8: Configure Static and Media Files

### 8.1 Create .htaccess for Static Files

Create `public_html/mobile-meals-center/.htaccess`:

```apache
# Passenger configuration
PassengerEnabled On
PassengerAppRoot /home/username/public_html/mobile-meals-center

# Python version
PassengerPython /home/username/public_html/mobile-meals-center/env/bin/python

# Static files
Alias /static /home/username/public_html/mobile-meals-center/staticfiles
<Directory /home/username/public_html/mobile-meals-center/staticfiles>
    Require all granted
</Directory>

# Media files
Alias /media /home/username/public_html/mobile-meals-center/media
<Directory /home/username/public_html/mobile-meals-center/media>
    Require all granted
</Directory>

# Redirect all requests to Passenger
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteRule ^(static|media)($|/) - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteRule ^(.*)$ passenger_wsgi.py [QSA,L]
</IfModule>
```

### 8.2 Set Permissions

```bash
chmod 755 passenger_wsgi.py
chmod -R 755 staticfiles/
chmod -R 755 media/
chmod -R 755 logs/
```

---

## Step 9: Restart Application

### Via cPanel
1. Go to **Setup Python App**
2. Find your application
3. Click **Restart**

### Via SSH
```bash
# Create/touch tmp/restart.txt to restart Passenger
mkdir -p tmp
touch tmp/restart.txt
```

---

## Step 10: Verify Deployment

1. Visit your domain: `https://yourdomain.com`
2. Check admin panel: `https://yourdomain.com/admin/`
3. Test user registration and login
4. Place a test order
5. Check logs: `logs/errors.log`

---

## Troubleshooting

### Issue 1: 500 Internal Server Error

**Check error logs:**
```bash
tail -f logs/errors.log
```

**Common causes:**
- Incorrect Python path in `passenger_wsgi.py`
- Missing dependencies
- Database connection issues
- DEBUG = True in production

### Issue 2: Static Files Not Loading

**Solution:**
```bash
# Collect static files again
python manage.py collectstatic --noinput

# Check .htaccess configuration
# Verify STATIC_ROOT path
```

### Issue 3: Database Connection Error

**Verify:**
- Database name, user, password in settings.py
- MySQL service is running
- User has correct privileges

```bash
# Test database connection
mysql -u niebzdyl_admin -p mobilemealscenter
```

### Issue 4: Permission Denied Errors

```bash
# Fix permissions
chmod -R 755 /home/username/public_html/mobile-meals-center
chown -R username:username /home/username/public_html/mobile-meals-center
```

### Issue 5: Module Not Found

```bash
# Reinstall requirements
source env/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## Production Checklist

- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured
- [ ] Database credentials secured
- [ ] Static files collected
- [ ] Media directory created with proper permissions
- [ ] Logs directory created
- [ ] Email settings configured
- [ ] SSL certificate installed
- [ ] Security settings enabled
- [ ] Superuser created
- [ ] Test orders placed successfully
- [ ] Email notifications working
- [ ] Backup strategy in place

---

## Maintenance

### Update Application

```bash
cd ~/public_html/mobile-meals-center
source env/bin/activate

# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
touch tmp/restart.txt
```

### Backup Database

```bash
# Create backup
mysqldump -u niebzdyl_admin -p mobilemealscenter > backup_$(date +%Y%m%d).sql

# Restore from backup
mysql -u niebzdyl_admin -p mobilemealscenter < backup_20260208.sql
```

### Monitor Logs

```bash
# Watch error log
tail -f logs/errors.log

# Check recent errors
tail -100 logs/errors.log

# Search for specific errors
grep "ERROR" logs/errors.log
```

---

## Performance Optimization

### 1. Enable Caching

Add to `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}
```

Create cache table:
```bash
python manage.py createcachetable
```

### 2. Optimize Database

```sql
-- Add indexes for frequently queried fields
ALTER TABLE orders_order ADD INDEX idx_status (status);
ALTER TABLE orders_order ADD INDEX idx_customer (customer_id);
ALTER TABLE orders_order ADD INDEX idx_restaurant (restaurant_id);
```

### 3. Enable Compression

Add to `.htaccess`:
```apache
# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>
```

---

## Security Best Practices

1. **Keep Django Updated**
   ```bash
   pip install --upgrade Django
   ```

2. **Use Environment Variables**
   - Never commit passwords to Git
   - Use `.env` file for sensitive data

3. **Regular Backups**
   - Daily database backups
   - Weekly full application backups

4. **Monitor Logs**
   - Check `logs/security.log` regularly
   - Set up alerts for critical errors

5. **SSL Certificate**
   - Use Let's Encrypt or cPanel AutoSSL
   - Force HTTPS in settings

---

## Support Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Passenger Documentation**: https://www.phusionpassenger.com/docs/
- **cPanel Documentation**: https://docs.cpanel.net/

---

## Contact

For deployment issues or questions:
- Email: admin@mobilemealscenter.com
- Phone: +254702502952

---

*Mobile Meals Center - Production Deployment Guide* 🚀
