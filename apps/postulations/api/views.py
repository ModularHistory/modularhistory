from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from apps.postulations.serializers import PostulationSerializer

from apps.postulations.models import Postulation


class PostulationViewSet(ModelViewSet):
    """API endpoint for viewing and editing postulations."""

    queryset = Postulation.objects.all()
    serializer_class = PostulationSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostulationListAPIView(ListAPIView):
    """API view for listing postulations."""

    queryset = Postulation.objects.all()
    serializer_class = PostulationSerializer
