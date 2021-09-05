from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.propositions.api.serializers import OccurrenceModelSerializer
from apps.propositions.models.occurrence import Occurrence


class OccurrenceViewSet(ModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OccurrenceAPIView(RetrieveAPIView):
    """API view for a single occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceModelSerializer
    lookup_field = 'slug'
