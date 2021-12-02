from typing import Union

from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.entities.models.entity import Entity
from apps.propositions.models.proposition import Proposition
from apps.search.documents.base import Document, InstantSearchDocumentFactory
from apps.search.documents.config import DEFAULT_INDEX_SETTINGS, html_field_analyzer
from apps.sources.models.source import Source


@registry.register_document
class PropositionDocument(Document):
    """ElasticSearch document for propositions."""

    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'propositions'

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
            'name': fields.TextField(),
            'aliases': fields.TextField(),
            'description': fields.TextField(analyzer=html_field_analyzer),
        },
    )

    class Django:
        model = Proposition
        related_models = [Source, Entity]

    def get_queryset(self):
        return super().get_queryset().prefetch_related('related_entities', 'sources', 'tags')

    def get_instances_from_related(self, related_instance: Union[Source, Entity]):
        try:
            return related_instance.propositions.all()
        except AttributeError:
            return related_instance.proposition_set.all()


PropositionInstantSearchDocument = InstantSearchDocumentFactory(
    model=Proposition, search_fields=['title'], filter_fields=['type']
)
