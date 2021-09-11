from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from core.api.views import ExtendedModelViewSet

from apps.places.api.serializers import PlaceDrfSerializer
from apps.places.models import Place


class PlaceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
