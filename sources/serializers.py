"""Serializers for the entities app."""

import serpy

from modularhistory.models.model import ModelSerializer
from search.models.searchable_model import SearchableModelSerializer


class SourceSerializer(SearchableModelSerializer):
    """Serializer for sources."""

    html = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.source'


class ContainmentSerializer(ModelSerializer):
    """Serializer for source containments."""

    phrase = serpy.Field()
    page_number = serpy.IntField()
    end_page_number = serpy.IntField()
    container = SourceSerializer()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.sourcecontainment'


class CitationSerializer(ModelSerializer):
    """Serializer for citations."""

    html = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.citation'
