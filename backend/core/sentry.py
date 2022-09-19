"""
This module initializes Sentry for error reporting.

It should be imported ONCE (and only once) by either settings.py or asgi.py.
"""

import logging

import sentry_sdk
from core.constants.environments import Environments
from core.environment import ENVIRONMENT, VERSION
from decouple import config
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

SEND_EVENTS = (
    config('SEND_SENTRY_EVENTS', cast=bool, default=False)
    if ENVIRONMENT == Environments.DEV
    else True
)

IGNORED_PATTERNS = ("No application configured for scope type 'lifespan'",)

SENTRY_ENVIRONMENT = config('SENTRY_ENVIRONMENT', default=ENVIRONMENT)


def filter(event, hint):
    """Filter events to be sent to Sentry."""
    error = str(hint)
    if SEND_EVENTS:
        for pattern in IGNORED_PATTERNS:
            if pattern in error:
                logging.info('Ignoring Sentry event: {error}')
        else:
            logging.info(f'Sending Sentry event: {error}')
            return event
    else:
        logging.info(f'Intercepted Sentry event: {hint.get("log_record") or hint}')
    return None


# Initialize the Sentry SDK for error reporting
SENTRY_DSN = config('SENTRY_BACKEND_DSN')
sentry_sdk.init(
    before_send=filter,
    # https://docs.sentry.io/platforms/python/configuration/options/#dsn
    dsn=SENTRY_DSN,
    # https://docs.sentry.io/platforms/python/configuration/environments/
    environment=SENTRY_ENVIRONMENT,
    # https://docs.sentry.io/platforms/python/configuration/integrations/
    integrations=[
        CeleryIntegration(),
        DjangoIntegration(),
        RedisIntegration(),
    ],
    # https://docs.sentry.io/platforms/python/configuration/releases/
    release=f'modularhistory@{VERSION}',
    # Associate users to errors (using django.contrib.auth):
    # https://docs.sentry.io/platforms/python/configuration/options/#send-default-pii
    send_default_pii=True,
    # https://docs.sentry.io/platforms/python/performance/
    traces_sample_rate=0.5,
)

# SentryAsgiMiddleware is imported and aliased so that it can be imported
# from this module (also initializing Sentry) by asgi.py as `SentryMiddleware`
from sentry_sdk.integrations.asgi import (  # noqa: F401, E402; type: ignore
    SentryAsgiMiddleware as SentryMiddleware,
)
