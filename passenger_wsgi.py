import os
import sys

# Fix for Unicode decode errors in Passenger
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add your project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add your virtual environment's site-packages to the sys.path
# Adjust the path to match your Python version (check with: python --version)
venv_path = os.path.join(project_home, 'virtualenv', 'mobile-meals-center', '3.12', 'lib', 'python3.12', 'site-packages')
if os.path.exists(venv_path) and venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Alternative: Try common virtual environment paths
possible_venv_paths = [
    os.path.join(project_home, 'env', 'lib', 'python3.12', 'site-packages'),
    os.path.join(project_home, 'env', 'lib', 'python3.11', 'site-packages'),
    os.path.join(os.path.expanduser('~'), 'virtualenv', 'mobile-meals-center', '3.12', 'lib', 'python3.12', 'site-packages'),
]

for path in possible_venv_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        break

# Set environment variable to tell Django where settings are
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()
