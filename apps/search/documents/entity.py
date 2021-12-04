from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.entities.models.entity import Entity
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, html_field_analyzer

from ...entities.models import Category
from .base import Document, InstantSearchDocumentFactory


@registry.register_document
class EntityDocument(Document):
    """ElasticSearch document for entities."""

    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'entities'

    name = fields.TextField()
    aliases = fields.TextField()
    description = fields.TextField(analyzer=html_field_analyzer)

    class Django:
        model = Entity


EntityInstantSearchDocument = InstantSearchDocumentFactory(Entity, ['name', 'aliases'])

EntityCategoryInstantSearchDocument = InstantSearchDocumentFactory(
    Category, ['name', 'aliases']
)
