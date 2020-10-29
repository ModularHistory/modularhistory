"""Constants usable throughout the ModularHistory application."""

from aenum import Constant


class ResponseCodes(Constant):
    """Response codes."""

    PERMANENT_REDIRECT = 301
    REDIRECT = 302
    SUCCESS = 200


class ModelNameSet(Constant):
    """Model name constants (to avoid magic strings)."""

    citation = 'citation'
    entity = 'entity'
    image = 'image'
    occurrence = 'occurrence'
    place = 'place'
    quote = 'quote'
    source = 'source'


MODEL_CLASS_PATHS = {
    ModelNameSet.citation: 'sources.models.Citation',
    ModelNameSet.entity: 'entities.models.Entity',
    ModelNameSet.image: 'images.models.Image',
    ModelNameSet.occurrence: 'occurrences.models.Occurrence',
    ModelNameSet.place: 'places.models.Place',
    ModelNameSet.quote: 'quotes.models.Quote',
    ModelNameSet.source: 'sources.models.Source',
}

CONTENT_TYPE_IDS = {
    ModelNameSet.citation: 118,
    ModelNameSet.entity: 14,
    ModelNameSet.image: 19,
    ModelNameSet.occurrence: 24,
    ModelNameSet.place: 41,
    ModelNameSet.quote: 49,
    ModelNameSet.source: 142,
}

OCCURRENCE_CT_ID = CONTENT_TYPE_IDS.get(ModelNameSet.occurrence)
QUOTE_CT_ID = CONTENT_TYPE_IDS.get(ModelNameSet.quote)
IMAGE_CT_ID = CONTENT_TYPE_IDS.get(ModelNameSet.image)
SOURCE_CT_ID = CONTENT_TYPE_IDS.get(ModelNameSet.source)

YES = 'Yes'
NO = 'No'
EMPTY_STRING = ''
SLASH = '/'
SPACE = ' '
COLON = ':'
COMMA = ','
PERIOD = '.'
NEW_LINE = '\n'

PDF_URL_PAGE_KEY = 'page'

MIGRATIONS_DIRNAME = 'migrations'
SQUASHED_MIGRATIONS_DIRNAME = 'squashed_migrations'

BASH_PLACEHOLDER = '{}'  # noqa: P103
NEGATIVE = 'n'
AFFIRMATIVE = 'y'
PROD_DB_ENV_VAR = 'USE_PROD_DB'
LOCAL = 'local'
PRODUCTION = 'production'
PROD_DB_ENV_VAR_VALUES = {LOCAL: '', PRODUCTION: 'True'}
MAX_MIGRATION_COUNT = 3

APPS_WITH_MIGRATIONS = (
    # 'account',  # affected by social_django
    'entities',
    'images',
    'markup',
    'occurrences',
    'places',
    'quotes',
    'search',
    'sources',
    'staticpages',
    'topics',
)

SOCIAL_AUTH_URL_NAME = 'social:begin'
