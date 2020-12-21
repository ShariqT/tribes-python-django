"""
ASGI config for tribes_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, ChannelNameRouter
from tribes_core.consumers import MessageConsumer
from channels.routing import get_default_application
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tribes_django.settings')
django.setup()

application = get_default_application()