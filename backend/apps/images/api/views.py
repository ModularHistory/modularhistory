from apps.images.api.serializers import ImageSerializer, VideoSerializer
from apps.images.models import Image, Video
from core.api.views import ExtendedModelViewSet


class ImageViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing images."""

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    list_fields = None


class VideoViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing videos."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    list_fields = None
