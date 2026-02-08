# MySQL Database Setup Guide

This guide will help you set up MySQL as the database for Mobile Meals Center.

## Prerequisites

1. **MySQL Server** installed on your system
2. **Python MySQL Client** (mysqlclient)

---

## Step 1: Install MySQL Server

### Windows
1. Download MySQL Community Server from: https://dev.mysql.com/downloads/mysql/
2. Run the installer and follow the setup wizard
3. During installation:
   - Choose "Developer Default" or "Server only"
   - Set a root password (remember this!)
   - Keep default port: 3306
   - Configure MySQL as a Windows Service

### Alternative: Using XAMPP
If you have XAMPP installed:
1. Start XAMPP Control Panel
2. Start the MySQL service
3. Default credentials: username=`root`, password=`` (empty)

---

## Step 2: Install Python MySQL Client

Open your terminal in the project directory and run:

```bash
pip install mysqlclient
```

### Troubleshooting Installation

**Windows Error: "Microsoft Visual C++ 14.0 is required"**

Option 1: Install Visual C++ Build Tools
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "Desktop development with C++"

Option 2: Use pre-compiled wheel
```bash
pip install --only-binary :all: mysqlclient
```

Option 3: Alternative MySQL connector
```bash
pip uninstall mysqlclient
pip install pymysql
```

If using PyMySQL, add this to `config/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Step 3: Create Database

### Using MySQL Command Line

1. Open MySQL command line:
```bash
mysql -u root -p
```

2. Enter your MySQL root password

3. Create the database:
```sql
CREATE DATABASE mobile_meals_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. (Optional) Create a dedicated user:
```sql
CREATE USER 'mealscenter'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON mobile_meals_db.* TO 'mealscenter'@'localhost';
FLUSH PRIVILEGES;
```

5. Exit MySQL:
```sql
EXIT;
```

### Using phpMyAdmin (if using XAMPP)

1. Open browser and go to: http://localhost/phpmyadmin
2. Click "New" in the left sidebar
3. Database name: `mobile_meals_db`
4. Collation: `utf8mb4_unicode_ci`
5. Click "Create"

---

## Step 4: Configure Django Settings

The database settings have been updated in `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mobile_meals_db',
        'USER': 'root',
        'PASSWORD': '',  # Set your MySQL password here
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

**Update the PASSWORD field** with your MySQL root password or dedicated user password.

### Using Environment Variables (Recommended for Production)

Create a `.env` file in your project root:
```
DB_NAME=mobile_meals_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

Install python-decouple:
```bash
pip install python-decouple
```

Update `settings.py`:
```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='mobile_meals_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

---

## Step 5: Run Migrations

Now that MySQL is configured, run the Django migrations:

```bash
# Make sure your virtual environment is activated
python manage.py makemigrations
python manage.py migrate
```

This will create all the necessary tables in your MySQL database.

---

## Step 6: Create Superuser

Create an admin user to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email
- Password

---

## Step 7: Verify Setup

1. Start the development server:
```bash
python manage.py runserver
```

2. Check if the server starts without errors

3. Access the admin panel: http://127.0.0.1:8000/admin/

4. Log in with your superuser credentials

---

## Database Management

### Viewing Database

**MySQL Command Line:**
```bash
mysql -u root -p
USE mobile_meals_db;
SHOW TABLES;
DESCRIBE accounts_user;
SELECT * FROM accounts_user;
```

**phpMyAdmin:**
- Go to http://localhost/phpmyadmin
- Select `mobile_meals_db` from the left sidebar
- Browse tables

### Backup Database

```bash
mysqldump -u root -p mobile_meals_db > backup.sql
```

### Restore Database

```bash
mysql -u root -p mobile_meals_db < backup.sql
```

### Reset Database

If you need to start fresh:

```bash
# Drop and recreate database
mysql -u root -p
DROP DATABASE mobile_meals_db;
CREATE DATABASE mobile_meals_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Run migrations again
python manage.py migrate
python manage.py createsuperuser
```

---

## Common Issues & Solutions

### Issue 1: "Access denied for user 'root'@'localhost'"
**Solution:** Check your MySQL password in `settings.py`

### Issue 2: "Can't connect to MySQL server"
**Solution:** 
- Ensure MySQL service is running
- Check if port 3306 is correct
- Verify HOST is 'localhost' or '127.0.0.1'

### Issue 3: "Unknown database 'mobile_meals_db'"
**Solution:** Create the database first (Step 3)

### Issue 4: "django.db.utils.OperationalError: (2003, "Can't connect...")"
**Solution:**
- Check if MySQL is running: `mysql --version`
- Restart MySQL service
- Windows: Services → MySQL → Restart
- XAMPP: Restart MySQL from control panel

### Issue 5: Character encoding issues
**Solution:** Ensure database uses utf8mb4:
```sql
ALTER DATABASE mobile_meals_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## Performance Optimization

### Enable Query Caching (Optional)

Add to `settings.py`:
```python
DATABASES = {
    'default': {
        # ... existing config ...
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
    }
}
```

### Database Indexing

Django automatically creates indexes for:
- Primary keys
- Foreign keys
- Fields with `db_index=True`

To add custom indexes, use migrations:
```python
python manage.py makemigrations --empty yourapp
```

---

## Switching from SQLite to MySQL

If you have existing data in SQLite:

### Option 1: Export/Import Data

```bash
# Export data from SQLite
python manage.py dumpdata > data.json

# Switch to MySQL (update settings.py)
# Run migrations
python manage.py migrate

# Import data to MySQL
python manage.py loaddata data.json
```

### Option 2: Manual Migration

1. Export specific models:
```bash
python manage.py dumpdata accounts > accounts.json
python manage.py dumpdata restaurants > restaurants.json
python manage.py dumpdata meals > meals.json
python manage.py dumpdata orders > orders.json
```

2. Switch to MySQL and migrate

3. Load data:
```bash
python manage.py loaddata accounts.json
python manage.py loaddata restaurants.json
python manage.py loaddata meals.json
python manage.py loaddata orders.json
```

---

## Production Considerations

### Security
1. **Never commit passwords** to version control
2. Use environment variables for sensitive data
3. Create a dedicated MySQL user (not root)
4. Use strong passwords
5. Limit user privileges to only what's needed

### Connection Pooling
Consider using connection pooling for production:
```bash
pip install django-db-connection-pool
```

### Monitoring
- Enable MySQL slow query log
- Monitor connection count
- Set up database backups (daily recommended)

---

## MySQL Configuration File

For production, optimize MySQL settings in `my.cnf` or `my.ini`:

```ini
[mysqld]
max_connections = 200
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
query_cache_size = 32M
```

Location:
- **Windows:** `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
- **Linux:** `/etc/mysql/my.cnf`

---

## Useful MySQL Commands

```sql
-- Show all databases
SHOW DATABASES;

-- Use specific database
USE mobile_meals_db;

-- Show all tables
SHOW TABLES;

-- Describe table structure
DESCRIBE table_name;

-- Show table size
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'mobile_meals_db'
ORDER BY (data_length + index_length) DESC;

-- Count records in all tables
SELECT 
    table_name,
    table_rows
FROM information_schema.tables
WHERE table_schema = 'mobile_meals_db';
```

---

## Next Steps

1. ✅ Install MySQL Server
2. ✅ Install mysqlclient package
3. ✅ Create database
4. ✅ Update settings.py with password
5. ✅ Run migrations
6. ✅ Create superuser
7. ✅ Test the application

---

## Support

If you encounter issues:
1. Check MySQL error logs
2. Enable Django DEBUG mode
3. Check Django logs
4. Verify MySQL service is running
5. Test MySQL connection independently

**MySQL Error Log Location:**
- Windows: `C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err`
- XAMPP: `xampp\mysql\data\*.err`

---

*Mobile Meals Center - MySQL Database Setup Complete* 🗄️✅
