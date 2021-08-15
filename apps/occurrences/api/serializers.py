from typing import TYPE_CHECKING

import serpy

from apps.search.api.serializers import SearchableModelSerializer

if TYPE_CHECKING:
    from apps.occurrences.models.occurrence import Occurrence
    from apps.propositions.models.proposition import Proposition


class OccurrenceSerializer(SearchableModelSerializer):
    """Serializer for occurrences."""

    proposition = serpy.MethodField()

    def get_model(self, instance: 'Occurrence') -> str:
        """Return the model name of the instance."""
        return 'occurrences.occurrence'

    def get_proposition(self, instance: 'Occurrence') -> dict:
        """Return the model name of the instance."""
        proposition: 'Proposition' = instance._proposition
        return proposition.serialize()
