"""Constants usable throughout the ModularHistory application."""

from aenum import Constant


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
SPACE = ' '
COLON = ':'
PERIOD = '.'

PDF_URL_PAGE_KEY = 'page'

SOCIAL_AUTH_URL_NAME = 'social:begin'
