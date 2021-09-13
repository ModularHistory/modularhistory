"""Serializers for the entities app."""
from apps.sources.models import Source, SourceContainment
from core.models.model import DrfModelSerializer
from core.models.module import DrfModuleSerializer


class SourceDrfSerializer(DrfModuleSerializer):
    """Serializer for sources."""

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'sources.source'

    class Meta(DrfModuleSerializer.Meta):
        model = Source
        fields = DrfModuleSerializer.Meta.fields + ['citation_html']


class ContainmentDrfSerializer(DrfModelSerializer):
    """Serializer for source containments."""

    container = SourceDrfSerializer()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.sourcecontainment'

    class Meta(DrfModelSerializer.Meta):
        model = SourceContainment
        fields = DrfModelSerializer.Meta.fields + [
            'phrase',
            'page_number',
            'end_page_number',
            'container',
        ]
