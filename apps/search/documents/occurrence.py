from apps.search.documents.config import DEFAULT_INDEX_SETTINGS

from .proposition import PropositionDocument


class OccurrenceDocument(PropositionDocument):
    class Index:
        settings = DEFAULT_INDEX_SETTINGS
        name = 'occurrences'

    def get_queryset(self):
        return super().get_queryset().filter(type='propositions.occurrence')
