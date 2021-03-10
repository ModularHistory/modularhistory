"""Constants usable throughout the ModularHistory application."""

from aenum import Constant


class ResponseCodes(Constant):
    """Response codes."""

    PERMANENT_REDIRECT = 301
    REDIRECT = 302
    SUCCESS = 200


PDF_URL_PAGE_KEY = 'page'

MIGRATIONS_DIRNAME = 'migrations'
SQUASHED_MIGRATIONS_DIRNAME = 'squashed'

LOCAL = 'local'
PRODUCTION = 'production'
MAX_MIGRATION_COUNT = 2

APPS_WITH_MIGRATIONS = (
    # 'account',
    'entities',
    'images',
    'markup',
    'occurrences',
    'places',
    'postulations',
    'quotes',
    'search',
    'sources',
    'staticpages',
    'topics',
)

SOCIAL_AUTH_URL_NAME = 'social:begin'
