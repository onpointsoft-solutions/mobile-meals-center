import os
import sys

# Fix for Unicode decode errors in Passenger
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add your project directory to the sys.path
project_home = '/home/niebzdyl/repositories/mobile-meals-center'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add your virtual environment's site-packages to the sys.path
# This is the critical part - must point to where Django is installed
venv_path = '/home/niebzdyl/virtualenv/mobilemealscenter/3.12/lib/python3.12/site-packages'
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Set environment variable to tell Django where settings are
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()
