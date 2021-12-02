from rest_framework.generics import RetrieveAPIView

from apps.moderation.serializers import get_moderated_model_serializer
from apps.propositions.api.serializers import PropositionSerializer
from apps.propositions.models import Proposition
from core.api.views import ExtendedModelViewSet


class PropositionViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing propositions."""

    queryset = Proposition.objects.all()
    serializer_class = PropositionSerializer

    def list(self, request, **kwargs):
        # get_absolute_url for occurrences currently returns a link with "propositions"
        # instead of "occurrences". For now, we work around this by allowing retrieval
        # of occurrences through the propositions API, but listing should exclude occurrences.
        self.queryset = self.queryset.filter(type='propositions.conclusions')
        return super().list(request, **kwargs)


class PropositionModerationAPIView(RetrieveAPIView):
    """API view for retrieving a proposition for moderation."""

    queryset = Proposition.objects.all()
    serializer_class = get_moderated_model_serializer(PropositionSerializer)
    lookup_field = 'slug'
