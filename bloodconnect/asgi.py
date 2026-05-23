"""
ASGI config for bloodconnect project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodconnect.settings')
application = get_asgi_application()
