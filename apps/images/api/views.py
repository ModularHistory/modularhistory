from apps.images.api.serializers import ImageDrfSerializer, VideoDrfSerializer
from apps.images.models import Image, Video
from core.api.views import ExtendedModelViewSet


class ImageViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing images."""

    queryset = Image.objects.all()
    serializer_class = ImageDrfSerializer
    list_fields = None


class VideoViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing videos."""

    queryset = Video.objects.all()
    serializer_class = VideoDrfSerializer
    list_fields = None
