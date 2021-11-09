from apps.sources.api.serializers import PageNumbersDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Piece
from apps.sources.models.sources.piece import PIECE_TYPES


class _PieceDrfSerializer(SourceDrfSerializer, PageNumbersDrfSerializerMixin):
    """Serializer for piece sources."""

    type_field_choices = PIECE_TYPES

    class Meta(SourceDrfSerializer.Meta):
        model = Piece
        fields = (
            SourceDrfSerializer.Meta.fields
            + PageNumbersDrfSerializerMixin.Meta.fields
            + ['type']
        )


class PieceDrfSerializer(_PieceDrfSerializer):
    """Serializer for piece sources."""

    originalEdition = _PieceDrfSerializer(read_only=True, source='original_edition')
