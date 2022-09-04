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


class RcloneStorageProviders(Constant):
    """Rclone storage provider ids."""

    GOOGLE_DRIVE = 'gdrive'
    MEGA = 'mega'
