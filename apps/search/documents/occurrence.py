from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from apps.search.documents.config import DEFAULT_INDEX_SETTINGS
from core.constants.content_types import ContentTypes

from .proposition import PropositionDocument


# @registry.register_document
class OccurrenceDocument(PropositionDocument):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'occurrences'

    def get_queryset(self):
        return super().get_queryset().filter(type='propositions.occurrence')
