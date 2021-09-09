from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.moderation.serializers import get_moderated_model_serializer
from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.propositions.models import Proposition


class PropositionViewSet(ModelViewSet):
    """API endpoint for viewing and editing propositions."""

    queryset = Proposition.objects.all()
    lookup_field = 'slug'
    serializer_class = PropositionDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request):
        # get_absolute_url for occurrences currently returns a link with "propositions"
        # instead of "occurrences". For now, we work around this by allowing retrieval
        # of occurrences through the propositions API, but listing should exclude occurrences.
        self.queryset = self.queryset.filter(type='propositions.conclusions')
        return super().list(request)


class PropositionModerationAPIView(RetrieveAPIView):
    """API view for retrieving a proposition for moderation."""

    queryset = Proposition.objects.all()
    serializer_class = get_moderated_model_serializer(PropositionDrfSerializer)
    lookup_field = 'slug'
