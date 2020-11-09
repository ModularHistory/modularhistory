"""Serializers for the entities app."""

import serpy

from modularhistory.models.model import ModelSerializer
from modularhistory.models.searchable_model import SearchableModelSerializer


class SourceSerializer(SearchableModelSerializer):
    """Serializer for sources."""

    html = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.source'


class CitationSerializer(ModelSerializer):
    """Serializer for citations."""

    html = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.citation'
