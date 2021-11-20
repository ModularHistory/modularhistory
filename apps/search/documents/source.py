from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, html_field_analyzer
from apps.sources.models.source import Source

from ...sources.models import Publication, SourceFile
from .base import Document, InstantSearchDocumentFactory


@registry.register_document
class SourceDocument(Document):
    """ElasticSearch document for sources."""

    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'sources'

    citation_string = fields.TextField(analyzer=html_field_analyzer)
    description = fields.TextField(analyzer=html_field_analyzer)
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
        model = Source


SourceInstantSearchDocument = InstantSearchDocumentFactory(
    model=Source,
    search_fields=['name'],  # TODO: should we keep mapping fields to 'name'?
    filter_fields=['model_name'],
    field_kwargs={
        'name': {
            'attr': 'citation_string'
        },  # TODO: decide if want to use other fields like title instead of citation_string
    },
)

SourcePublicationInstantSearchDocument = InstantSearchDocumentFactory(
    model=Publication, search_fields=['name']
)

SourceFileInstantSearchDocument = InstantSearchDocumentFactory(
    model=SourceFile, search_fields=['name']
)
