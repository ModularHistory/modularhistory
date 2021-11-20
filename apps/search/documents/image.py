from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.images.models import Image
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, html_field_analyzer

from .base import Document, InstantSearchDocumentFactory


@registry.register_document
class ImageDocument(Document):
    """ElasticSearch document for images."""

    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'images'

    caption = fields.TextField(analyzer=html_field_analyzer)
    description = fields.TextField(analyzer=html_field_analyzer)
    provider = fields.TextField()

    class Django:
        model = Image


ImageInstantSearchDocument = InstantSearchDocumentFactory(
    model=Image,
    search_fields=['name'],
    filter_fields=['image_type'],
    field_kwargs={
        'name': {'attr': '__str__'}
    },  # TODO: decide if want to use something else for name
)
