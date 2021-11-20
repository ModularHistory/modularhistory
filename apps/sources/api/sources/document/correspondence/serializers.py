from apps.dates.api.fields import HistoricDateTimeDrfField
from apps.sources.api.serializers import DocumentDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Correspondence


class _CorrespondenceDrfSerializer(SourceDrfSerializer, DocumentDrfSerializerMixin):
    """Serializer for correspondence document sources."""

    instant_search_fields = SourceDrfSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.correspondence'},
        },
    }

    date = HistoricDateTimeDrfField(write_only=True, required=False)

    class Meta(SourceDrfSerializer.Meta):
        model = Correspondence
        fields = (
            SourceDrfSerializer.Meta.fields
            + DocumentDrfSerializerMixin.Meta.fields
            + ['type', 'recipient']
        )


class CorrespondenceDrfSerializer(_CorrespondenceDrfSerializer):
    """Serializer for correspondence document sources."""

    original_edition_serialized = _CorrespondenceDrfSerializer(
        read_only=True, source='original_edition'
    )
