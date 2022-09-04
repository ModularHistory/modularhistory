from apps.sources.api.sources.film.serializers import FilmSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Film


class FilmViewSet(SourceViewSet):
    """API endpoint for viewing and editing film sources."""

    queryset = Film.objects.all()
    serializer_class = FilmSerializer
