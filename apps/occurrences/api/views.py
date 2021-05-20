from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.occurrences.models.occurrence import Occurrence
from apps.occurrences.serializers import OccurrenceSerializer


class OccurrenceViewSet(ModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer


class OccurrenceListAPIView(ListAPIView):
    """API view for listing occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer


class OccurrenceAPIView(RetrieveAPIView):
    """API view for a single occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer
    lookup_field = 'slug'
