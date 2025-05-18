"""
ASGI config for hangout_streak project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Initialize Django ASGI application early to ensure the AppRegistry is populated
# before importing code that may import ORM models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hangout_streak.settings')
django.setup()

from events import routing as events_routing
from chat import routing as chat_routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                events_routing.websocket_urlpatterns +
                chat_routing.websocket_urlpatterns
            )
        )
    ),
})
