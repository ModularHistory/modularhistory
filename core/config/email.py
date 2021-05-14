"""Settings for email."""

from decouple import config

DEFAULT_EMAIL_PORT = 25

# https://docs.djangoproject.com/en/3.1/topics/email/
# https://docs.djangoproject.com/en/3.1/ref/settings#s-email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config(
    'EMAIL_PORT',
    default=DEFAULT_EMAIL_PORT,
    cast=lambda port: int(port) if port else DEFAULT_EMAIL_PORT,
)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True
