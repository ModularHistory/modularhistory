from apps.dates.api.fields import HistoricDateTimeField
from apps.sources.api.serializers import DocumentSerializerMixin, SourceSerializer
from apps.sources.models import Correspondence


class _CorrespondenceSerializer(SourceSerializer, DocumentSerializerMixin):
    """Serializer for correspondence document sources."""

    instant_search_fields = SourceSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.correspondence'},
        },
    }

    date = HistoricDateTimeField(write_only=True, required=False)

    class Meta(SourceSerializer.Meta):
        model = Correspondence
        fields = (
            SourceSerializer.Meta.fields
            + DocumentSerializerMixin.Meta.fields
            + ['type', 'recipient']
        )


class CorrespondenceSerializer(_CorrespondenceSerializer):
    """Serializer for correspondence document sources."""

    original_edition_serialized = _CorrespondenceSerializer(
        read_only=True, source='original_edition'
    )
