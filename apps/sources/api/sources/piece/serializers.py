from apps.sources.api.serializers import PageNumbersSerializerMixin, SourceSerializer
from apps.sources.models import Piece


class _PieceSerializer(SourceSerializer, PageNumbersSerializerMixin):
    """Serializer for piece sources."""

    class Meta(SourceSerializer.Meta):
        model = Piece
        fields = SourceSerializer.Meta.fields + PageNumbersSerializerMixin.Meta.fields


class PieceSerializer(_PieceSerializer):
    """Serializer for piece sources."""

    originalEdition = _PieceSerializer(read_only=True, source='original_edition')
