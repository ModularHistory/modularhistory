from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.entities.models.entity import Entity
from apps.search.documents.config import (
    DEFAULT_INDEX_SETTINGS,
    get_index_name_for_ct,
    html_field_analyzer,
)
from core.constants.content_types import ContentTypes

from .base import Document


@registry.register_document
class EntityDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = get_index_name_for_ct(ContentTypes.entity)

    name = fields.TextField()
    aliases = fields.TextField()
    description = fields.TextField(
        attr='description.raw_value', analyzer=html_field_analyzer
    )

    class Django:
        model = Entity
