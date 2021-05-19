"""Constants usable throughout the ModularHistory application."""

from aenum import Constant
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache


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


class ContentTypes(Constant):
    """Content type name constants (to avoid magic strings)."""

    citation = 'sources.citation'
    entity = 'entities.entity'
    image = 'images.image'
    occurrence = 'occurrences.occurrence'
    place = 'places.place'
    quote = 'quotes.quote'
    source = 'sources.source'
    topic = 'topics.topic'
    postulation = 'postulations.postulation'


MODEL_CLASS_PATHS = {
    ModelNameSet.citation: 'apps.sources.models.Citation',
    ModelNameSet.entity: 'apps.entities.models.Entity',
    ModelNameSet.image: 'apps.images.models.Image',
    ModelNameSet.occurrence: 'apps.occurrences.models.NewOccurrence',
    ModelNameSet.place: 'apps.places.models.Place',
    ModelNameSet.quote: 'apps.quotes.models.Quote',
    ModelNameSet.source: 'apps.sources.models.Source',
    ModelNameSet.fact: 'apps.postulations.models.Postulation',
    ModelNameSet.postulation: 'apps.postulations.models.Postulation',
}


def get_ct_id(ct_name: str) -> int:
    """Return the content type id for the given content type name."""
    cache_key = f'{ct_name}_ct_id'
    cached_ct_id = cache.get(cache_key)
    if cached_ct_id:
        ct_id = cached_ct_id
    else:
        app_label, model = ct_name.split('.')
        ct_id = ContentType.objects.get_by_natural_key(
            app_label=app_label, model=model
        ).id
        cache.set(cache_key, ct_id, timeout=None)
    return ct_id
