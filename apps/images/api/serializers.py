"""Serializers for the entities app."""

from apps.images.models import Image
from core.models.module import DrfModuleSerializer


class ImageDrfSerializer(DrfModuleSerializer):
    """Serializer for images."""

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'images.image'

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
