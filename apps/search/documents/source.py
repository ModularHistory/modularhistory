from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import html_strip
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS

from apps.sources.models import Source


@registry.register_document
class SourceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'sources'

    citation = fields.TextField(attr='citation_string', analyzer=html_strip)
    description = fields.TextField(attr='description.raw_value', analyzer=html_strip)

    class Django:
        model = Source
