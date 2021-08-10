from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.propositions.api.serializers import PropositionSerializer
from apps.propositions.models import Proposition


class PropositionListAPIView(ListAPIView):
    """API view for listing propositions."""

    queryset = Proposition.objects.filter(
        type='propositions.conclusion', hidden=False, verified=True
    )
    serializer_class = PropositionSerializer


class PropositionAPIView(RetrieveAPIView):
    """API view for a single occurrences."""

    queryset = Proposition.objects.all()
    serializer_class = PropositionSerializer
    lookup_field = 'slug'
