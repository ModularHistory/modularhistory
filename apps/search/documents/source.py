from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, html_field_analyzer
from apps.sources.models.source import Source

from .base import Document


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
            'key': fields.TextField(),
            'aliases': fields.TextField(),
            'description': fields.TextField(analyzer=html_field_analyzer),
            'path': fields.TextField(),
        },
    )

    class Django:
        model = Source
