from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import (
    DEFAULT_INDEX_SETTINGS,
    get_index_name_for_ct,
    html_field_analyzer,
)
from apps.sources.models import Source
from core.constants.content_types import ContentTypes

from .base import Document


@registry.register_document
class SourceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = get_index_name_for_ct(ContentTypes.source)

    citation = fields.TextField(attr='citation_string', analyzer=html_field_analyzer)
    description = fields.TextField(
        attr='description.raw_value', analyzer=html_field_analyzer
    )

    class Django:
        model = Source
