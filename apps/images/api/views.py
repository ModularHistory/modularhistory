from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.images.api.serializers import ImageDrfSerializer
from apps.images.models import Image


class ImageViewSet(ModelViewSet):
    """API endpoint for viewing and editing images."""

    queryset = Image.objects.all()
    serializer_class = ImageDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
