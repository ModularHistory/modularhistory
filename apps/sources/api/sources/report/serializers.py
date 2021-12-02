from apps.sources.api.serializers import SourceSerializer, TextualSerializerMixin
from apps.sources.models import Report


class _ReportSerializer(SourceSerializer, TextualSerializerMixin):
    """Serializer for report sources."""

    class Meta(SourceSerializer.Meta):
        model = Report
        fields = (
            SourceSerializer.Meta.fields
            + TextualSerializerMixin.Meta.fields
            + [
                'publisher',
                'number',
            ]
        )


class ReportSerializer(_ReportSerializer):
    """Serializer for report sources."""

    originalEdition = _ReportSerializer(read_only=True, source='original_edition')
