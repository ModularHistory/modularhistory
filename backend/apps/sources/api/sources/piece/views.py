from apps.sources.api.sources.piece.serializers import PieceSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Piece


class PieceViewSet(SourceViewSet):
    """API endpoint for viewing and editing piece sources."""

    queryset = Piece.objects.all()
    serializer_class = PieceSerializer
