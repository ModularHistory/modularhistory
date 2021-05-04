from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import html_field_analyzer
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS

from apps.quotes.models import Quote
from apps.entities.models import Entity
from apps.sources.models import Source


@registry.register_document
class QuoteDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'quotes'

    text = fields.TextField(attr='text.raw_value', analyzer=html_field_analyzer)
    context = fields.TextField(attr='context.raw_value', analyzer=html_field_analyzer)
    date = fields.TextField(attr='date.string')
    attributees = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.raw_value')
    })
    citations = fields.TextField(attr='citation_html', analyzer=html_field_analyzer)
    topics = fields.ObjectField(attr='_related_topics', properties={
        'id': fields.IntegerField(),
        'key': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.raw_value', analyzer=html_field_analyzer)
    })

    class Django:
        model = Quote
        related_models = [Source, Entity]

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'attributees', 'sources', 'topics'
        )
