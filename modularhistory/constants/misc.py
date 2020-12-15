"""Constants usable throughout the ModularHistory application."""

from aenum import Constant


class Environments(Constant):
    """Environments."""

    PROD = 'prod'
    GITHUB_TEST = 'test'
    DEV = 'dev'
    DEV_DOCKER = 'dev_docker'


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
    topic = 'topic'
    fact = 'fact'
    postulation = 'postulation'


MODEL_CLASS_PATHS = {
    ModelNameSet.citation: 'apps.sources.models.Citation',
    ModelNameSet.entity: 'apps.entities.models.Entity',
    ModelNameSet.image: 'apps.images.models.Image',
    ModelNameSet.occurrence: 'apps.occurrences.models.Occurrence',
    ModelNameSet.place: 'apps.places.models.Place',
    ModelNameSet.quote: 'apps.quotes.models.Quote',
    ModelNameSet.source: 'apps.sources.models.Source',
    ModelNameSet.fact: 'apps.postulations.models.Postulation',
    ModelNameSet.postulation: 'apps.postulations.models.Postulation',
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

PDF_URL_PAGE_KEY = 'page'

MIGRATIONS_DIRNAME = 'migrations'
SQUASHED_MIGRATIONS_DIRNAME = 'squashed'

LOCAL = 'local'
PRODUCTION = 'production'
MAX_MIGRATION_COUNT = 2

APPS_WITH_MIGRATIONS = (
    # 'account',  # affected by social_django
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
