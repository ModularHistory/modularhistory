from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.places.models import Place
from apps.places.serializers import PlaceSerializer


class PlaceViewSet(ModelViewSet):
    """API endpoint for viewing and editing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class PlaceListAPIView(ListAPIView):
    """API view for listing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
