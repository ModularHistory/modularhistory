from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from modularhistory.views import AsyncAPIViewMixin
from apps.images.serializers import ImageSerializer

from apps.images.models import Image


class ImageViewSet(ModelViewSet):
    """API endpoint for viewing and editing images."""

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImageListAPIView(AsyncAPIViewMixin, ListAPIView):
    """API view for listing images."""

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
