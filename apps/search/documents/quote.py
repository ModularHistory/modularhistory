from typing import Union

from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.entities.models.entity import Entity
from apps.quotes.models.quote import Quote
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, html_field_analyzer
from apps.sources.models.source import Source

from .base import Document, InstantSearchDocumentFactory


@registry.register_document
class QuoteDocument(Document):
    """ElasticSearch document for quotes."""

    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'quotes'

    text = fields.TextField(analyzer=html_field_analyzer)
    context = fields.TextField(analyzer=html_field_analyzer)
    attributees = fields.ObjectField(
        properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(),
            'aliases': fields.TextField(),
            'description': fields.TextField(),
        }
    )
    citations = fields.TextField(attr='citation_html', analyzer=html_field_analyzer)
    topics = fields.ObjectField(
        attr='cached_tags',
        properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(),
            'aliases': fields.TextField(),
            'description': fields.TextField(analyzer=html_field_analyzer),
        },
    )

    class Django:
        model = Quote
        related_models = [Source, Entity]

    def get_queryset(self):
        return super().get_queryset().prefetch_related('attributees', 'sources', 'topics')

    def get_instances_from_related(self, related_instance: Union[Source, Entity]):
        return related_instance.quotes.all()


QuoteInstantSearchDocument = InstantSearchDocumentFactory(
    model=Quote,
    search_fields=['name'],
    field_kwargs={
        'name': {'attr': '__str__'}
    },  # TODO: we might want just to use 'title' field
)
