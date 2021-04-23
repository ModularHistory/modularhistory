from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer

from apps.occurrences.models import Occurrence
from apps.quotes.models import Quote
from apps.entities.models import Entity
from apps.sources.models import Source
from apps.images.models import Image

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "porter_stem"],
    char_filter=["html_strip"]
)

DEFAULT_INDEX_SETTINGS = {'number_of_shards': 1, 'number_of_replicas': 0}


@registry.register_document
class QuoteDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'quotes'

    text = fields.TextField(attr='text.text', analyzer=html_strip)
    context = fields.TextField(attr='context.text', analyzer=html_strip)
    date = fields.TextField(attr='date.string')
    attributees = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.text')
    })
    citations = fields.TextField(attr='citation_html', analyzer=html_strip)
    topics = fields.ObjectField(attr='_related_topics', properties={
        'id': fields.IntegerField(),
        'key': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.text', analyzer=html_strip)
    })

    class Django:
        model = Quote
        related_models = [Source, Entity]

    def get_queryset(self):
        return super(QuoteDocument, self).get_queryset().prefetch_related(
            'attributees', 'sources', 'topics'
        )


@registry.register_document
class OccurrenceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'occurrences'

    summary = fields.TextField(attr='summary.text', analyzer=html_strip)
    description = fields.TextField(attr='description.text', analyzer=html_strip)
    date = fields.TextField(attr='date.string')
    involved_entities = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.text')
    })
    citations = fields.TextField(attr='citation_html', analyzer=html_strip)
    topics = fields.ObjectField(attr='_related_topics', properties={
        'id': fields.IntegerField(),
        'key': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.text', analyzer=html_strip)
    })

    class Django:
        model = Occurrence
        related_models = [Source, Entity]

    def get_queryset(self):
        return super(OccurrenceDocument, self).get_queryset().prefetch_related(
            'involved_entities', 'sources', 'topics'
        )


@registry.register_document
class EntityDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'entities'

    name = fields.TextField()
    aliases = fields.TextField()
    description = fields.TextField(attr='description.text', analyzer=html_strip)

    class Django:
        model = Entity


@registry.register_document
class SourceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'sources'

    citation = fields.TextField(attr='citation_string', analyzer=html_strip)
    description = fields.TextField(attr='description.text', analyzer=html_strip)

    class Django:
        model = Source


@registry.register_document
class ImageDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'images'

    caption = fields.TextField(attr='caption.text', analyzer=html_strip)
    description = fields.TextField(attr='description.text', analyzer=html_strip)
    provider = fields.TextField(attr='provider')

    class Django:
        model = Image
