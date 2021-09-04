"""Serializers for the entities app."""

from apps.sources.models import AbstractCitation, Source
from core.models.model import ModelSerializerDrf
from core.models.module import ModuleSerializerDrf


class SourceModelSerializer(ModuleSerializerDrf):
    """Serializer for sources."""

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'sources.source'

    class Meta(ModuleSerializerDrf.Meta):
        model = Source
        fields = ModuleSerializerDrf.Meta.fields + ['citation_html']


class ContainmentModelSerializer(ModelSerializerDrf):
    """Serializer for source containments."""

    container = SourceModelSerializer()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.sourcecontainment'

    class Meta(ModelSerializerDrf.Meta):
        model = Source
        fields = ModelSerializerDrf.Meta.fields + [
            'phrase',
            'page_number',
            'end_page_number',
            'container',
        ]


class CitationModelSerializer(ModelSerializerDrf):
    """Serializer for citations."""

    class Meta(ModelSerializerDrf.Meta):
        model = AbstractCitation
        fields = ModelSerializerDrf.Meta.fields + ['html']
