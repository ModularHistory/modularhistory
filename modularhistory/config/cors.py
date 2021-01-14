"""Settings related to cross-origin requests."""

# https://github.com/adamchainz/django-cors-headers

# NOTE: This setting is intended to aid development. In production, all
# static files should be served by the webserver, rendering CORS unnecessary.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://react:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "localhost",
    "react",
]
