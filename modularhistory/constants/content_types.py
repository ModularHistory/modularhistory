"""Constants usable throughout the ModularHistory application."""

from aenum import Constant
from django.contrib.contenttypes.models import ContentType


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


OCCURRENCE_CT_ID = ContentType.objects.get_by_natural_key(
    app_label='occurrences', model='occurrence'
)
QUOTE_CT_ID = ContentType.objects.get_by_natural_key(app_label='quotes', model='quote')
