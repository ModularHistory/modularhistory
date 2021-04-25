from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import html_strip
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS

from apps.occurrences.models import Occurrence
from apps.entities.models import Entity
from apps.sources.models import Source


@registry.register_document
class OccurrenceDocument(Document):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'occurrences'

    summary = fields.TextField(attr='summary.raw_value', analyzer=html_strip)
    description = fields.TextField(attr='description.raw_value', analyzer=html_strip)
    date = fields.TextField(attr='date.string')
    involved_entities = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.raw_value')
    })
    citations = fields.TextField(attr='citation_html', analyzer=html_strip)
    topics = fields.ObjectField(attr='_related_topics', properties={
        'id': fields.IntegerField(),
        'key': fields.TextField(),
        'aliases': fields.TextField(),
        'description': fields.TextField(attr='description.raw_value', analyzer=html_strip)
    })

    class Django:
        model = Occurrence
        related_models = [Source, Entity]

    def get_queryset(self):
        return super(OccurrenceDocument, self).get_queryset().prefetch_related(
            'involved_entities', 'sources', 'topics'
        )
