from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.propositions.api.serializers import PropositionSerializer
from apps.propositions.models import PolymorphicProposition


class PropositionViewSet(ModelViewSet):
    """API endpoint for viewing and editing propositions."""

    queryset = PolymorphicProposition.objects.all()
    serializer_class = PropositionSerializer


class PropositionListAPIView(ListAPIView):
    """API view for listing propositions."""

    queryset = PolymorphicProposition.objects.filter(hidden=False, verified=True)
    serializer_class = PropositionSerializer
