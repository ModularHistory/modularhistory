from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.propositions.api.serializers import PropositionSerializer
from apps.propositions.models import TypedProposition


class PropositionViewSet(ModelViewSet):
    """API endpoint for viewing and editing propositions."""

    queryset = TypedProposition.objects.all()
    serializer_class = PropositionSerializer


class PropositionListAPIView(ListAPIView):
    """API view for listing propositions."""

    queryset = TypedProposition.objects.all()
    serializer_class = PropositionSerializer
