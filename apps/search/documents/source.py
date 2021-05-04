from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import html_field_analyzer
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS

from apps.sources.models import Source


@registry.register_document
class SourceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'sources'

    citation = fields.TextField(attr='citation_string', analyzer=html_field_analyzer)
    description = fields.TextField(attr='description.raw_value', analyzer=html_field_analyzer)

    class Django:
        model = Source
