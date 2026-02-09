import os
import sys

# 🔧 settings module (VERY IMPORTANT)
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

# 🔧 load django wsgi application
from config.wsgi import application
