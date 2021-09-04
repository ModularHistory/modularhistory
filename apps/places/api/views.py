from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.places.api.serializers import PlaceModelSerializer
from apps.places.models import Place


class PlaceViewSet(ModelViewSet):
    """API endpoint for viewing and editing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
