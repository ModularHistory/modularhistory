"""Serializers for the entities app."""

from drf_extra_fields.fields import HybridImageField

from apps.dates.api.fields import HistoricDateTimeDrfField
from apps.images.models import Image, Video
from apps.images.models.media_model import MediaModel
from core.models.serializers import DrfModuleSerializer


class MediaModelDrfSerializer(DrfModuleSerializer):
    """Serializer for media models."""

    date = HistoricDateTimeDrfField(write_only=True, required=False)
    end_date = HistoricDateTimeDrfField(write_only=True, required=False)

    class Meta(DrfModuleSerializer.Meta):
        model = MediaModel
        fields = DrfModuleSerializer.Meta.fields + [
            'date',
            'end_date',
            'date_string',
            'caption',
            'description',
            'provider',
            'caption_html',
            'description_html',
        ]
        extra_kwargs = DrfModuleSerializer.Meta.extra_kwargs | {
            'caption': {'write_only': True},
            'description': {'required': False, 'write_only': True},
            'provider': {'required': False, 'write_only': True},
        }


class ImageDrfSerializer(MediaModelDrfSerializer):
    """Serializer for images."""

    image = HybridImageField()

    class Meta(MediaModelDrfSerializer.Meta):
        model = Image
        fields = MediaModelDrfSerializer.Meta.fields + [
            'provider_string',
            'image',
            'src_url',
            'width',
            'height',
            'bg_img_position',
            'urls',
        ]
        extra_kwargs = MediaModelDrfSerializer.Meta.extra_kwargs | {
            'image': {'write_only': True},
        }


class VideoDrfSerializer(MediaModelDrfSerializer):
    """Serializer for videos."""

    class Meta(MediaModelDrfSerializer.Meta):
        model = Video
        fields = MediaModelDrfSerializer.Meta.fields + ['url', 'embed_code', 'duration']
        extra_kwargs = MediaModelDrfSerializer.Meta.extra_kwargs | {
            'url': {'allow_null': False}
        }
