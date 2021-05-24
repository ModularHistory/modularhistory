from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.propositions.api.serializers import OccurrenceSerializer
from apps.propositions.models.occurrence import Occurrence


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
