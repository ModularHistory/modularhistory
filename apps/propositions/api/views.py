from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from core.api.views import ExtendedModelViewSet

from apps.moderation.serializers import get_moderated_model_serializer
from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.propositions.models import Proposition


class PropositionViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing propositions."""

    queryset = Proposition.objects.filter(type='propositions.conclusion')
    serializer_class = PropositionDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PropositionModerationAPIView(RetrieveAPIView):
    """API view for retrieving a proposition for moderation."""

    queryset = Proposition.objects.all()
    serializer_class = get_moderated_model_serializer(PropositionDrfSerializer)
    lookup_field = 'slug'
