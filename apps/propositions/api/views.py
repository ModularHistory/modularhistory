from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.propositions.models import Proposition
from core.api.views import ExtendedModelViewSet


class PropositionViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing propositions."""

    queryset = Proposition.objects.all()
    serializer_class = PropositionDrfSerializer

    def list(self, request, **kwargs):
        # get_absolute_url for occurrences currently returns a link with "propositions"
        # instead of "occurrences". For now, we work around this by allowing retrieval
        # of occurrences through the propositions API, but listing should exclude occurrences.
        self.queryset = self.queryset.filter(type='propositions.conclusion')
        return super().list(request, **kwargs)
