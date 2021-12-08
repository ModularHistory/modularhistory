from apps.sources.api.serializers import PageNumbersSerializerMixin, SourceSerializer
from apps.sources.models import Piece


class _PieceSerializer(SourceSerializer, PageNumbersSerializerMixin):
    """Serializer for piece sources."""

    instant_search_fields = SourceSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.piece'},
        },
    }

    class Meta(SourceSerializer.Meta):
        model = Piece
        fields = (
            SourceSerializer.Meta.fields + PageNumbersSerializerMixin.Meta.fields + ['type']
        )


class PieceSerializer(_PieceSerializer):
    """Serializer for piece sources."""

    original_edition_serialized = _PieceSerializer(read_only=True, source='original_edition')
