"""Settings related to cross-origin requests."""

from core.constants.environments import Environments
from core.environment import ENVIRONMENT

# https://github.com/adamchainz/django-cors-headers

# NOTE: This setting is intended to aid development. In production, all
# static files should be served by the webserver, rendering CORS unnecessary.
CORS_ALLOWED_ORIGINS = [
    # Nginx reverse proxy
    'http://localhost',
    'http://127.0.0.1',
    'http://modularhistory.dev.net',
    # Frontend server
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://next:3000',
    # Backend server
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://django:8000',
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
