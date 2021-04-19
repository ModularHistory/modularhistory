from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.images.models import Image
from apps.images.serializers import ImageSerializer


class ImageViewSet(ModelViewSet):
    """API endpoint for viewing and editing images."""

    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class ImageListAPIView(ListAPIView):
    """API view for listing images."""

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
