from apps.sources.api.serializers import PageNumbersDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Piece


class _PieceDrfSerializer(SourceDrfSerializer, PageNumbersDrfSerializerMixin):
    """Serializer for piece sources."""

    instant_search_fields = SourceDrfSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.piece'},
        },
    }

    class Meta(SourceDrfSerializer.Meta):
        model = Piece
        fields = (
            SourceDrfSerializer.Meta.fields
            + PageNumbersDrfSerializerMixin.Meta.fields
            + ['type']
        )


class PieceDrfSerializer(_PieceDrfSerializer):
    """Serializer for piece sources."""

    original_edition_serialized = _PieceDrfSerializer(
        read_only=True, source='original_edition'
    )
