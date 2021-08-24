from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.moderation.serializers import get_moderated_model_serializer
from apps.propositions.api.serializers import PropositionSerializer
from apps.propositions.models import Proposition


class PropositionListAPIView(ListAPIView):
    """API view for listing propositions."""

    queryset = Proposition.objects.filter(type='propositions.conclusion', verified=True)
    serializer_class = PropositionSerializer


class PropositionAPIView(RetrieveAPIView):
    """API view for retrieving a proposition."""

    queryset = Proposition.objects.all()
    serializer_class = PropositionSerializer
    lookup_field = 'slug'


class PropositionModerationAPIView(RetrieveAPIView):
    """API view for retrieving a proposition for moderation."""

    queryset = Proposition.objects.all()
    serializer_class = get_moderated_model_serializer(Proposition)
    lookup_field = 'slug'
