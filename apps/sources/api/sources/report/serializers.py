from apps.sources.api.serializers import SourceDrfSerializer, TextualDrfSerializerMixin
from apps.sources.models import Report


class _ReportDrfSerializer(SourceDrfSerializer, TextualDrfSerializerMixin):
    """Serializer for report sources."""

    instant_search_fields = SourceDrfSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.report'},
        },
    }

    class Meta(SourceDrfSerializer.Meta):
        model = Report
        fields = (
            SourceDrfSerializer.Meta.fields
            + TextualDrfSerializerMixin.Meta.fields
            + [
                'publisher',
                'number',
            ]
        )


class ReportDrfSerializer(_ReportDrfSerializer):
    """Serializer for report sources."""

    original_edition_serialized = _ReportDrfSerializer(
        read_only=True, source='original_edition'
    )
