"""
ASGI config for history project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

from channels.auth import AuthMiddlewareStack

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.chat import routing

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'https': get_asgi_application(),
        'websocket': AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)),
    }
)
