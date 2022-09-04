from apps.places.api.serializers import PlaceSerializer
from apps.places.models import Place
from core.api.views import ExtendedModelViewSet


class PlaceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    list_fields = None
