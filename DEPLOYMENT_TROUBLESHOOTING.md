# Deployment Troubleshooting Guide

## Current Error: ModuleNotFoundError: No module named 'django'

This error means Django is not installed in the virtual environment that Passenger is using.

---

## Solution Steps

### Step 1: SSH into Your Server

```bash
ssh niebzdyl@yourdomain.com
```

### Step 2: Navigate to Project Directory

```bash
cd ~/repositories/mobile-meals-center
```

### Step 3: Check Virtual Environment Location

Your virtual environment should be at:
```
/home/niebzdyl/virtualenv/mobilemealscenter/3.12/
```

Verify it exists:
```bash
ls -la ~/virtualenv/mobilemealscenter/3.12/
```

### Step 4: Activate Virtual Environment

```bash
source ~/virtualenv/mobilemealscenter/3.12/bin/activate
```

You should see `(mobilemealscenter)` in your prompt.

### Step 5: Verify Python Version

```bash
python --version
```

Should show Python 3.12.x

### Step 6: Install Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Django>=5.0,<5.1
- Pillow>=10.0.0
- django-crispy-forms>=2.0
- crispy-bootstrap5>=0.7
- stripe>=7.0.0
- pymysql>=1.1.0

### Step 7: Verify Django Installation

```bash
python -c "import django; print(django.get_version())"
```

Should print Django version (e.g., 5.0.x)

### Step 8: Check Site-Packages Path

```bash
python -c "import site; print(site.getsitepackages())"
```

This should show paths like:
```
['/home/niebzdyl/virtualenv/mobilemealscenter/3.12/lib/python3.12/site-packages']
```

### Step 9: Verify passenger_wsgi.py Paths

The `passenger_wsgi.py` file should have these exact paths:

```python
project_home = '/home/niebzdyl/repositories/mobile-meals-center'
venv_path = '/home/niebzdyl/virtualenv/mobilemealscenter/3.12/lib/python3.12/site-packages'
```

### Step 10: Run Database Migrations

```bash
python manage.py migrate
```

### Step 11: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 12: Test Django Locally

```bash
python manage.py check
```

Should show: "System check identified no issues (0 silenced)."

### Step 13: Restart Passenger Application

```bash
mkdir -p tmp
touch tmp/restart.txt
```

Or via cPanel:
1. Go to **Setup Python App**
2. Find your application
3. Click **Restart**

---

## Alternative: If Virtual Environment Doesn't Exist

If the virtual environment doesn't exist at the expected location:

### Create New Virtual Environment

```bash
cd ~
python3.12 -m venv virtualenv/mobilemealscenter/3.12
```

### Activate and Install

```bash
source ~/virtualenv/mobilemealscenter/3.12/bin/activate
cd ~/repositories/mobile-meals-center
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Common Issues

### Issue 1: Wrong Python Version

**Check:**
```bash
python --version
```

**Fix:**
Use the correct Python version:
```bash
python3.12 -m venv ~/virtualenv/mobilemealscenter/3.12
```

### Issue 2: Virtual Environment Path Mismatch

**Check passenger_wsgi.py:**
The `venv_path` must match the actual location.

**Find actual path:**
```bash
source ~/virtualenv/mobilemealscenter/3.12/bin/activate
python -c "import site; print(site.getsitepackages()[0])"
```

**Update passenger_wsgi.py** with the correct path.

### Issue 3: Permissions Issues

**Fix permissions:**
```bash
chmod -R 755 ~/repositories/mobile-meals-center
chmod 644 ~/repositories/mobile-meals-center/passenger_wsgi.py
```

### Issue 4: Multiple Python Versions

**Check available Python versions:**
```bash
ls -la /usr/bin/python*
```

**Use specific version:**
```bash
/usr/bin/python3.12 -m venv ~/virtualenv/mobilemealscenter/3.12
```

---

## Verification Checklist

After following the steps above, verify:

- [ ] Virtual environment exists at correct path
- [ ] Django is installed: `pip list | grep Django`
- [ ] All requirements installed: `pip list`
- [ ] passenger_wsgi.py has correct paths
- [ ] Database credentials correct in settings.py
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Application restarted via tmp/restart.txt

---

## Debug Commands

### Check if Django is importable:
```bash
source ~/virtualenv/mobilemealscenter/3.12/bin/activate
python -c "import django; print('Django OK:', django.__file__)"
```

### Check sys.path in Python:
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

### List installed packages:
```bash
pip list
```

### Check passenger_wsgi.py syntax:
```bash
python passenger_wsgi.py
```

### View Passenger error log:
```bash
tail -50 ~/logs/passenger.log
# or
tail -50 /var/log/apache2/error_log
```

---

## cPanel Python App Configuration

If using cPanel's Python App interface:

1. **Application root**: `/home/niebzdyl/repositories/mobile-meals-center`
2. **Application URL**: `/` or your domain
3. **Application startup file**: `passenger_wsgi.py`
4. **Application Entry point**: `application`
5. **Python version**: 3.12

**Environment variables:**
- `DJANGO_SETTINGS_MODULE` = `config.settings`

---

## Final Test

After everything is set up:

```bash
# Activate environment
source ~/virtualenv/mobilemealscenter/3.12/bin/activate

# Navigate to project
cd ~/repositories/mobile-meals-center

# Test imports
python -c "from config.wsgi import application; print('WSGI OK')"

# Test Django
python manage.py check

# Restart
touch tmp/restart.txt
```

Then visit your domain in a browser.

---

## Contact Information

If issues persist after following this guide:
- Check logs: `~/logs/` or `/var/log/`
- Review error messages carefully
- Ensure all paths are absolute (not relative)
- Verify file permissions

---

*Mobile Meals Center - Deployment Troubleshooting* 🔧
