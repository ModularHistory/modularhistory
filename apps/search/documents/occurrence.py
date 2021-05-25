from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.entities.models.entity import Entity
from apps.propositions.models.occurrence import Occurrence
from apps.search.documents.base import Document
from apps.search.documents.config import (
    DEFAULT_INDEX_SETTINGS,
    get_index_name_for_ct,
    html_field_analyzer,
)
from apps.sources.models.source import Source
from core.constants.content_types import ContentTypes


@registry.register_document
class OccurrenceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = get_index_name_for_ct(ContentTypes.occurrence)

    title = fields.TextField(analyzer=html_field_analyzer)
    summary = fields.TextField(analyzer=html_field_analyzer)
    elaboration = fields.TextField(analyzer=html_field_analyzer)
    related_entities = fields.ObjectField(
        properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(),
            'aliases': fields.TextField(),
            'description': fields.TextField(),
        }
    )
    citations = fields.TextField(attr='citation_html', analyzer=html_field_analyzer)
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
        model = Occurrence
        related_models = [Source, Entity]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related('related_entities', 'sources', 'tags')
        )
