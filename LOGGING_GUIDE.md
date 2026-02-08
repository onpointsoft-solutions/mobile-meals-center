# Logging System Guide - Mobile Meals Center

## Overview

The application now has a comprehensive logging system that records all important events, errors, and activities across different modules.

---

## Log Files Location

All logs are stored in the `logs/` directory:

```
mobile-meals-center/
├── logs/
│   ├── general.log       # General application logs
│   ├── errors.log        # All errors and exceptions
│   ├── orders.log        # Order-related activities
│   ├── payments.log      # Payment transactions
│   ├── emails.log        # Email sending activities
│   ├── security.log      # Security warnings and issues
│   └── database.log      # Database queries and warnings
```

**Note:** The `logs/` directory is automatically created when the server starts and is excluded from Git (in `.gitignore`).

---

## Log File Details

### 1. **general.log** (10 MB, 5 backups)
Records general application activities:
- Server startup/shutdown
- User registrations
- Profile updates
- Restaurant creation
- Meal additions
- General Django operations

**Example:**
```
[INFO] 2026-02-08 17:30:15 accounts views register_user - New user registered: john@example.com
[INFO] 2026-02-08 17:31:22 restaurants views create_restaurant - Restaurant created: Pizza Palace
```

### 2. **errors.log** (10 MB, 5 backups)
Captures all errors and exceptions:
- HTTP 500 errors
- Database errors
- Form validation errors
- Template errors
- Unhandled exceptions

**Example:**
```
[ERROR] 2026-02-08 17:45:30 django.request log_response - Internal Server Error: /orders/create/
Traceback (most recent call last):
  File "orders/views.py", line 120, in form_valid
    ...
ValueError: Invalid order data
```

### 3. **orders.log** (5 MB, 3 backups)
Tracks order lifecycle:
- Order creation
- Order status changes
- Order cancellations
- Cart operations

**Example:**
```
[INFO] 2026-02-08 18:00:45 orders views OrderCreateView - Order created: ORD-2024-001
[INFO] 2026-02-08 18:15:20 orders views UpdateOrderStatusView - Order ORD-2024-001 status changed to confirmed
```

### 4. **payments.log** (5 MB, 3 backups)
Records payment transactions:
- Payment intent creation
- Payment confirmations
- Payment failures
- Refunds
- Cash on delivery confirmations

**Example:**
```
[INFO] 2026-02-08 18:01:00 payments views CreatePaymentIntentView - Payment created for order ORD-2024-001: KES 1,250.00
[INFO] 2026-02-08 18:01:15 payments views CreatePaymentIntentView - Cash on delivery confirmed for order ORD-2024-001
```

### 5. **emails.log** (5 MB, 3 backups)
Logs email sending activities:
- Order confirmations sent
- Restaurant notifications sent
- Email failures
- SMTP errors

**Example:**
```
[INFO] 2026-02-08 18:01:20 core.email_utils send_order_confirmation_email - Order confirmation email sent to customer@example.com for order ORD-2024-001
[INFO] 2026-02-08 18:01:22 core.email_utils send_restaurant_notification_email - Restaurant notification email sent to restaurant@example.com for order ORD-2024-001
[ERROR] 2026-02-08 18:05:30 core.email_utils send_order_confirmation_email - Failed to send email: SMTP connection failed
```

### 6. **security.log** (5 MB, 5 backups)
Security-related warnings:
- Failed login attempts
- Permission denied errors
- CSRF failures
- Suspicious activities

**Example:**
```
[WARNING] 2026-02-08 19:00:00 django.security csrf - CSRF verification failed
[WARNING] 2026-02-08 19:05:15 accounts views login - Failed login attempt for user: admin
```

### 7. **database.log** (10 MB, 3 backups)
Database operations (set to WARNING by default):
- Slow queries
- Database connection issues
- Migration warnings

**To log all SQL queries**, change in `settings.py`:
```python
'django.db.backends': {
    'handlers': ['file_database'],
    'level': 'DEBUG',  # Change from WARNING to DEBUG
    'propagate': False,
},
```

---

## Log Rotation

Logs automatically rotate when they reach their size limit:

| Log File | Max Size | Backups |
|----------|----------|---------|
| general.log | 10 MB | 5 |
| errors.log | 10 MB | 5 |
| orders.log | 5 MB | 3 |
| payments.log | 5 MB | 3 |
| emails.log | 5 MB | 3 |
| security.log | 5 MB | 5 |
| database.log | 10 MB | 3 |

**Example rotation:**
```
general.log          (current)
general.log.1        (previous)
general.log.2        (older)
general.log.3        (older)
general.log.4        (older)
general.log.5        (oldest - will be deleted on next rotation)
```

---

## Viewing Logs

### Real-time Monitoring (Windows)

**PowerShell:**
```powershell
Get-Content logs\errors.log -Wait -Tail 50
```

**Command Prompt:**
```cmd
type logs\errors.log
```

### Search Logs

**Find specific errors:**
```powershell
Select-String -Path logs\errors.log -Pattern "ERROR"
```

**Find by date:**
```powershell
Select-String -Path logs\general.log -Pattern "2026-02-08"
```

**Find payment issues:**
```powershell
Select-String -Path logs\payments.log -Pattern "failed"
```

### Linux/Mac

**Real-time monitoring:**
```bash
tail -f logs/errors.log
```

**Search logs:**
```bash
grep "ERROR" logs/errors.log
grep "2026-02-08" logs/general.log
```

---

## Adding Logging to Your Code

### Import Logger

```python
import logging

logger = logging.getLogger(__name__)
```

### Log Levels

```python
# DEBUG - Detailed diagnostic information
logger.debug('Detailed debug information')

# INFO - General informational messages
logger.info('User logged in successfully')

# WARNING - Warning messages
logger.warning('Disk space running low')

# ERROR - Error messages
logger.error('Failed to process payment')

# CRITICAL - Critical errors
logger.critical('Database connection lost')
```

### Example Usage

**In views.py:**
```python
import logging

logger = logging.getLogger(__name__)

class OrderCreateView(CreateView):
    def form_valid(self, form):
        logger.info(f'Creating order for user: {self.request.user.username}')
        
        try:
            order = form.save()
            logger.info(f'Order created successfully: {order.order_number}')
            return redirect('orders:detail', pk=order.pk)
        except Exception as e:
            logger.error(f'Failed to create order: {str(e)}', exc_info=True)
            messages.error(self.request, 'Failed to create order')
            return self.form_invalid(form)
```

**In models.py:**
```python
import logging

logger = logging.getLogger(__name__)

class Order(models.Model):
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'New order saved: {self.order_number}')
        else:
            logger.info(f'Order updated: {self.order_number}')
```

---

## Log Format

### Verbose Format (File Logs)
```
[LEVEL] TIMESTAMP MODULE FUNCTION - MESSAGE
```

**Example:**
```
[INFO] 2026-02-08 18:00:45 orders views OrderCreateView - Order created: ORD-2024-001
```

### Simple Format (Console)
```
[LEVEL] TIMESTAMP - MESSAGE
```

**Example:**
```
[INFO] 2026-02-08 18:00:45 - Order created: ORD-2024-001
```

---

## Troubleshooting

### Logs Not Being Created

1. **Check permissions:**
   - Ensure the application has write permissions to the `logs/` directory
   
2. **Check settings:**
   - Verify `LOGGING` configuration in `settings.py`
   - Ensure `DEBUG = True` for development

3. **Restart server:**
   ```bash
   python manage.py runserver
   ```

### Log Files Too Large

1. **Reduce log level:**
   ```python
   'level': 'WARNING',  # Instead of INFO or DEBUG
   ```

2. **Reduce max file size:**
   ```python
   'maxBytes': 1024 * 1024 * 2,  # 2 MB instead of 10 MB
   ```

3. **Increase backup count:**
   ```python
   'backupCount': 10,  # Keep more old logs
   ```

### Missing Logs

1. **Check logger name:**
   ```python
   logger = logging.getLogger(__name__)  # Correct
   logger = logging.getLogger('mylogger')  # May not be configured
   ```

2. **Check log level:**
   ```python
   logger.debug('This message')  # Won't show if level is INFO or higher
   logger.info('This message')   # Will show if level is INFO or lower
   ```

---

## Production Recommendations

### 1. Centralized Logging

Consider using a log aggregation service:
- **Sentry** - Error tracking and monitoring
- **Loggly** - Cloud-based log management
- **Papertrail** - Log aggregation and search
- **ELK Stack** - Elasticsearch, Logstash, Kibana

### 2. Log Rotation Schedule

Set up automated log cleanup:

**Windows Task Scheduler:**
```powershell
# Delete logs older than 30 days
Get-ChildItem logs\*.log.* | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

**Linux Cron:**
```bash
# Add to crontab
0 0 * * * find /path/to/logs -name "*.log.*" -mtime +30 -delete
```

### 3. Security

- **Never log sensitive data** (passwords, credit cards, API keys)
- **Sanitize user input** before logging
- **Restrict log file access** (file permissions)
- **Encrypt logs** in production if required

### 4. Performance

- **Use async logging** for high-traffic applications
- **Set appropriate log levels** (WARNING/ERROR in production)
- **Monitor disk space** regularly

---

## Monitoring Dashboard

### Create a Simple Log Viewer

**logs_viewer.py:**
```python
import os
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

@method_decorator(staff_member_required, name='dispatch')
class LogsViewer(TemplateView):
    template_name = 'admin/logs_viewer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logs_dir = settings.LOGS_DIR
        
        log_files = {}
        for filename in os.listdir(logs_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(logs_dir, filename)
                with open(filepath, 'r') as f:
                    # Read last 100 lines
                    lines = f.readlines()[-100:]
                    log_files[filename] = ''.join(lines)
        
        context['log_files'] = log_files
        return context
```

---

## Quick Reference

### Common Log Patterns

```python
# User actions
logger.info(f'User {user.username} performed action: {action}')

# Errors with traceback
logger.error(f'Error message', exc_info=True)

# Performance monitoring
import time
start = time.time()
# ... code ...
logger.info(f'Operation took {time.time() - start:.2f} seconds')

# Conditional logging
if settings.DEBUG:
    logger.debug(f'Debug info: {data}')
```

### Log Analysis Commands

```powershell
# Count errors by type
Select-String -Path logs\errors.log -Pattern "ERROR" | Group-Object Line

# Find slow operations
Select-String -Path logs\general.log -Pattern "took.*seconds"

# Monitor specific user
Select-String -Path logs\general.log -Pattern "user@example.com"
```

---

## Best Practices

1. ✅ **Log important events** (orders, payments, user actions)
2. ✅ **Include context** (user ID, order number, timestamps)
3. ✅ **Use appropriate levels** (INFO for normal, ERROR for failures)
4. ✅ **Don't log sensitive data** (passwords, tokens, credit cards)
5. ✅ **Keep messages clear** and actionable
6. ✅ **Include stack traces** for errors (`exc_info=True`)
7. ✅ **Monitor logs regularly** for issues
8. ✅ **Set up alerts** for critical errors

---

*Mobile Meals Center - Logging System Active* 📝✅
