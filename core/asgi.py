"""
ASGI config for history project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from typing import Callable

from django.core.asgi import get_asgi_application

# Fetch Django ASGI application early to ensure AppRegistry is populated.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from apps.chat import routing  # noqa: E402
from core.sentry import SentryMiddleware  # noqa: E402


class LifespanApp:
    """Temporary shim for https://github.com/django/channels/issues/1216."""

    def __init__(self, scope: dict):
        """Construct the shim."""
        self.scope = scope

    async def __call__(self, receive: Callable, send: Callable):
        """Respond to calls."""
        if self.scope['type'] == 'lifespan':
            while True:
                message = await receive()
                message_type = message['type']
                try:
                    stage = message_type.split('.')[1]
                except IndexError:
                    continue
                if stage not in {'startup', 'shutdown'}:
                    continue
                await send({'type': f'lifespan.{stage}.complete'})
                if stage == 'shutdown':
                    return


application = SentryMiddleware(
    ProtocolTypeRouter(
        {
            'http': django_asgi_app,
            'websocket': AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)),
            'lifespan': LifespanApp,
        }
    )
)
