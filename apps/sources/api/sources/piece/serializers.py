from apps.sources.api.serializers import PageNumbersDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Piece


class PieceDrfSerializer(SourceDrfSerializer, PageNumbersDrfSerializerMixin):
    """Serializer for piece sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Piece
        fields = SourceDrfSerializer.Meta.fields + PageNumbersDrfSerializerMixin.Meta.fields
