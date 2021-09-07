"""Serializers for the entities app."""

import serpy

from core.models.model import ModelSerializer
from core.models.module import ModuleSerializer


class SourceSerializer(ModuleSerializer):
    """Serializer for sources."""

    citation_html = serpy.StrField()
    title = serpy.StrField()

    def get_model(self, instance) -> str:
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


class CitationSerializer(serpy.Serializer):
    """Serializer for citations."""

    id = serpy.IntField()
    html = serpy.Field()
