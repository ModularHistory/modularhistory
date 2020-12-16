"""
ASGI config for history project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from apps.chat import routing
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from modularhistory.sentry import SentryAsgiMiddleware

from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')


application = SentryAsgiMiddleware(
    ProtocolTypeRouter(
        {
            'http': get_asgi_application(),
            'websocket': AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
            # Just HTTP for now. (We can add other protocols later.)
        }
    )
)
