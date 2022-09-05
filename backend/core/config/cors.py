"""Settings related to cross-origin requests."""

from core.constants.environments import Environments
from core.environment import ENVIRONMENT
from django.conf import settings

# https://github.com/adamchainz/django-cors-headers

# NOTE: This setting is intended to aid development. In production, all
# static files should be served by the webserver, rendering CORS unnecessary.
CORS_ALLOWED_ORIGINS = [
    # Nginx reverse proxy
    'http://localhost',
    'http://127.0.0.1',
    'http://modularhistory.dev.net',
    # Frontend server
    'http://localhost:3002',
    'http://127.0.0.1:3002',
    'http://next:3002',
    # Backend server
    f'http://localhost:{settings.PORT}',
    f'http://127.0.0.1:{settings.PORT}',
    f'http://django:{settings.PORT}',
]

CORS_ALLOW_ALL_ORIGINS = ENVIRONMENT == Environments.DEV
CORS_ALLOW_CREDENTIALS = CORS_ALLOW_ALL_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    '127.0.0.1',
    'localhost',
    'modularhistory.dev.net',
    'django',
    'next',
]
