from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from core.constants.content_types import ContentTypes
from apps.search.documents.config import html_field_analyzer, DEFAULT_INDEX_SETTINGS, get_index_name_for_ct

from apps.occurrences.models import Occurrence
from apps.entities.models import Entity
from apps.sources.models import Source

from apps.search.documents.base import Document


@registry.register_document
class OccurrenceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = get_index_name_for_ct(ContentTypes.occurrence)

    summary = fields.TextField(attr='summary.raw_value', analyzer=html_field_analyzer)
    description = fields.TextField(attr='description.raw_value', analyzer=html_field_analyzer)
    date_year = fields.IntegerField(attr='date.year')
    involved_entities = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.raw_value')
    })
    citations = fields.TextField(attr='citation_html', analyzer=html_field_analyzer)
    topics = fields.ObjectField(attr='_related_topics', properties={
        'id': fields.IntegerField(),
        'key': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.raw_value', analyzer=html_field_analyzer),
        'path': fields.TextField(),
    })

    class Django:
        model = Occurrence
        related_models = [Source, Entity]

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'involved_entities', 'sources', 'topics'
        )
