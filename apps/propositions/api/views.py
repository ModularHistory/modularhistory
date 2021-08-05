from rest_framework.generics import ListAPIView

from apps.propositions.api.serializers import PropositionSerializer
from apps.propositions.models import Proposition


class PropositionListAPIView(ListAPIView):
    """API view for listing propositions."""

    queryset = Proposition.objects.filter(
        type='propositions.conclusion', hidden=False, verified=True
    )
    serializer_class = PropositionSerializer
