from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.images.models import Image
from apps.search.documents.config import (
    DEFAULT_INDEX_SETTINGS,
    get_index_name_for_ct,
    html_field_analyzer,
)
from core.constants.content_types import ContentTypes

from .base import Document


@registry.register_document
class ImageDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = get_index_name_for_ct(ContentTypes.image)

    caption = fields.TextField(analyzer=html_field_analyzer)
    description = fields.TextField(analyzer=html_field_analyzer)
    provider = fields.TextField(attr='provider')

    class Django:
        model = Image
