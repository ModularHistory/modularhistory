from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import html_strip
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS

from apps.entities.models import Entity


@registry.register_document
class EntityDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'entities'

    name = fields.TextField()
    aliases = fields.TextField()
    description = fields.TextField(attr='description.raw_value', analyzer=html_strip)

    class Django:
        model = Entity