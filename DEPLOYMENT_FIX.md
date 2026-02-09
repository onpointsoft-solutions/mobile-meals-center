# Deployment Error Fixes

## Current Errors

### Error 1: Table doesn't exist
```
django.db.utils.ProgrammingError: (1146, "Table 'niebzdyl_mobilemealscenter.meals_category' doesn't exist")
```

### Error 2: Unicode decode error
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc0 in position 1: invalid start byte
```

---

## Solutions Applied

### 1. Fixed passenger_wsgi.py
- Added UTF-8 codec handling to fix unicode errors
- Updated virtual environment path to match server structure: `virtualenv/mobile-meals-center/3.12/`
- Added fallback paths for different Python versions

### 2. Added PyMySQL Configuration
- Updated `config/__init__.py` to use PyMySQL as MySQL driver
- Added `pymysql>=1.1.0` to requirements.txt
- PyMySQL is easier to install on shared hosting (no C compiler needed)

### 3. Database Tables Missing - Need to Run Migrations

---

## Steps to Fix on Server

### Step 1: SSH into Your Server

```bash
ssh niebzdyl@yourdomain.com
cd ~/mobile-meals-center
```

### Step 2: Activate Virtual Environment

```bash
# For cPanel virtual environment
source ~/virtualenv/mobile-meals-center/3.12/bin/activate

# Or if you created it manually
source env/bin/activate
```

### Step 3: Install PyMySQL

```bash
pip install pymysql
```

### Step 4: Run Migrations (CRITICAL)

This will create all the missing database tables:

```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, meals, orders, payments, restaurants, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying accounts.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  ...
  Applying meals.0001_initial... OK
  Applying orders.0001_initial... OK
  Applying payments.0001_initial... OK
  Applying restaurants.0001_initial... OK
  Applying sessions.0001_initial... OK
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: admin
- Email: admin@mobilemealscenter.com
- Password: (choose a strong password)

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 7: Restart Application

```bash
mkdir -p tmp
touch tmp/restart.txt
```

Or via cPanel:
1. Go to **Setup Python App**
2. Find your application
3. Click **Restart**

---

## Verify Database Tables Created

```bash
mysql -u niebzdyl_admin -p niebzdyl_mobilemealscenter
```

Then run:
```sql
SHOW TABLES;
```

You should see tables like:
- accounts_user
- meals_category
- meals_meal
- orders_order
- payments_payment
- restaurants_restaurant
- etc.

Exit MySQL:
```sql
EXIT;
```

---

## Common Issues After Migration

### Issue: "No module named 'pymysql'"

**Solution:**
```bash
source ~/virtualenv/mobile-meals-center/3.12/bin/activate
pip install pymysql
touch tmp/restart.txt
```

### Issue: "Access denied for user"

**Solution:**
Check database credentials in `config/settings.py`:
```python
'NAME': 'niebzdyl_mobilemealscenter',  # Should match your database name
'USER': 'niebzdyl_admin',
'PASSWORD': '@Admin@20266',
```

### Issue: Still getting unicode errors

**Solution:**
The updated `passenger_wsgi.py` should fix this. If not, add to `.htaccess`:
```apache
SetEnv LC_ALL en_US.UTF-8
SetEnv LANG en_US.UTF-8
```

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic --noinput
chmod -R 755 staticfiles/
```

---

## Verification Checklist

After running migrations, verify:

- [ ] Visit homepage: `https://yourdomain.com`
- [ ] Admin panel works: `https://yourdomain.com/admin/`
- [ ] Can log in with superuser
- [ ] No database errors in logs
- [ ] Static files loading correctly
- [ ] Can create test restaurant
- [ ] Can add meals
- [ ] Can place test order

---

## Check Logs for Errors

```bash
# View error log
tail -50 logs/errors.log

# Watch logs in real-time
tail -f logs/errors.log

# Check Passenger error log (if available)
tail -50 ~/passenger.log
```

---

## Database Backup (Before Migration)

If you have existing data, backup first:

```bash
mysqldump -u niebzdyl_admin -p niebzdyl_mobilemealscenter > backup_before_migration.sql
```

Restore if needed:
```bash
mysql -u niebzdyl_admin -p niebzdyl_mobilemealscenter < backup_before_migration.sql
```

---

## Quick Command Reference

```bash
# Activate virtual environment
source ~/virtualenv/mobile-meals-center/3.12/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Restart application
touch tmp/restart.txt

# Check Python version
python --version

# List installed packages
pip list

# Test database connection
python manage.py dbshell
```

---

## If Migrations Fail

### Option 1: Check Migration Files

```bash
# List migration files
ls -la */migrations/

# Check for migration conflicts
python manage.py showmigrations
```

### Option 2: Fake Initial Migrations (if tables partially exist)

```bash
python manage.py migrate --fake-initial
```

### Option 3: Reset Migrations (DANGER - only if database is empty)

```bash
# Drop all tables
mysql -u niebzdyl_admin -p niebzdyl_mobilemealscenter

DROP DATABASE niebzdyl_mobilemealscenter;
CREATE DATABASE niebzdyl_mobilemealscenter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Run migrations fresh
python manage.py migrate
```

---

## Contact Support

If issues persist:
1. Check `logs/errors.log` for detailed error messages
2. Verify all files uploaded correctly
3. Ensure virtual environment is activated
4. Check database credentials
5. Verify Python version matches (3.12)

---

*Run migrations to create database tables and fix deployment errors* 🔧
