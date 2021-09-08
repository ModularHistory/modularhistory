from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.moderation.serializers import get_moderated_model_serializer
from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.propositions.models import Proposition


class PropositionViewSet(ModelViewSet):
    """API endpoint for viewing and editing propositions."""

    queryset = Proposition.objects.filter(type='propositions.conclusion')
    lookup_field = 'slug'
    serializer_class = PropositionDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PropositionModerationAPIView(RetrieveAPIView):
    """API view for retrieving a proposition for moderation."""

    queryset = Proposition.objects.all()
    serializer_class = get_moderated_model_serializer(PropositionDrfSerializer)
    lookup_field = 'slug'
