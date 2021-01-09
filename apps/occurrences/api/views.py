from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from apps.occurrences.serializers import OccurrenceSerializer

from apps.occurrences.models import Occurrence


class OccurrenceViewSet(ModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class OccurrenceListAPIView(ListAPIView):
    """API view for listing occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer
