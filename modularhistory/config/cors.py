"""Settings related to cross-origin requests."""

# https://github.com/adamchainz/django-cors-headers

# NOTE: This setting is intended to aid development. In production, all
# static files should be served by the webserver, rendering CORS unnecessary.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://react:3000",
    "http://dev:8000",
    "http://django:8001",
]

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    "localhost",
    "django",
    "react",
]
