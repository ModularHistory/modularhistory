"""Serializers for the entities app."""

from apps.images.models import Image
from core.models.serializers import DrfModuleSerializer


class ImageDrfSerializer(DrfModuleSerializer):
    """Serializer for images."""

    class Meta(DrfModuleSerializer.Meta):
        model = Image
        fields = DrfModuleSerializer.Meta.fields + [
            'src_url',
            'width',
            'height',
            'caption_html',
            'provider_string',
            'bg_img_position',
        ]
