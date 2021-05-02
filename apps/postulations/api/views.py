from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.postulations.models import Postulation
from apps.postulations.serializers import PostulationSerializer


class PostulationViewSet(ModelViewSet):
    """API endpoint for viewing and editing postulations."""

    queryset = Postulation.objects.all()
    serializer_class = PostulationSerializer


class PostulationListAPIView(ListAPIView):
    """API view for listing postulations."""

    queryset = Postulation.objects.all()
    serializer_class = PostulationSerializer
