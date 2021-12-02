from apps.sources.api.serializers import SourceSerializer, TextualSerializerMixin
from apps.sources.models import Report


class _ReportSerializer(SourceSerializer, TextualSerializerMixin):
    """Serializer for report sources."""

    instant_search_fields = SourceSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.report'},
        },
    }

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

    original_edition_serialized = _ReportSerializer(
        read_only=True, source='original_edition'
    )
