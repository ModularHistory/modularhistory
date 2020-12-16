"""
ASGI config for history project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Fetch Django ASGI application early to ensure AppRegistry is populated.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')
django_asgi_app = get_asgi_application()

from apps.chat import routing  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from modularhistory.sentry import SentryAsgiMiddleware  # noqa: E402

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402


application = SentryAsgiMiddleware(
    ProtocolTypeRouter(
        {
            'http': django_asgi_app,
            'websocket': AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
            # Just HTTP for now. (We can add other protocols later.)
        }
    )
)
