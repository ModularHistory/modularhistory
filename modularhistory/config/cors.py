"""Settings related to cross-origin requests."""

from modularhistory.environment import environment
from modularhistory.constants.environments import Environments

# https://github.com/adamchainz/django-cors-headers

# NOTE: This setting is intended to aid development. In production, all
# static files should be served by the webserver, rendering CORS unnecessary.
CORS_ALLOWED_ORIGINS = [
    # Nginx reverse proxy
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://dev",
    # Frontend server
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://react:3000",
    # Backend server
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://django:8000",
]

CORS_ALLOW_ALL_ORIGINS = environment == Environments.DEV
CORS_ALLOW_CREDENTIALS = CORS_ALLOW_ALL_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    "127.0.0.1",
    "localhost",
    "django",
    "react",
]
