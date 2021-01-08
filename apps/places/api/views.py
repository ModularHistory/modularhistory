from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from modularhistory.views import AsyncAPIViewMixin
from apps.places.serializers import PlaceSerializer

from apps.places.models import Place


class PlaceViewSet(ModelViewSet):
    """API endpoint for viewing and editing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]


class PlaceListAPIView(AsyncAPIViewMixin, ListAPIView):
    """API view for listing places."""

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
