from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.places.api.serializers import PlaceDrfSerializer
from apps.places.models import Place
from core.api.views import ExtendedModelViewSet


class PlaceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    list_fields = None
