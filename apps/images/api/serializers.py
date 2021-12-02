"""Serializers for the entities app."""

from drf_extra_fields.fields import HybridImageField

from apps.dates.api.fields import HistoricDateTimeField
from apps.images.models import Image, Video
from apps.images.models.media_model import MediaModel
from core.models.serializers import ModuleSerializer


class MediaModelSerializer(ModuleSerializer):
    """Serializer for media models."""

    date = HistoricDateTimeField(write_only=True, required=False)
    end_date = HistoricDateTimeField(write_only=True, required=False)

    class Meta(ModuleSerializer.Meta):
        model = MediaModel
        fields = ModuleSerializer.Meta.fields + [
            'date',
            'end_date',
            'date_string',
            'caption',
            'description',
            'provider',
            'caption_html',
            'description_html',
        ]
        extra_kwargs = ModuleSerializer.Meta.extra_kwargs | {
            'caption': {'write_only': True},
            'description': {'required': False, 'write_only': True},
            'provider': {'required': False, 'write_only': True},
        }


class ImageSerializer(MediaModelSerializer):
    """Serializer for images."""

    image = HybridImageField()

    class Meta(MediaModelSerializer.Meta):
        model = Image
        fields = MediaModelSerializer.Meta.fields + [
            'provider_string',
            'image',
            'src_url',
            'width',
            'height',
            'bg_img_position',
            'urls',
        ]
        extra_kwargs = MediaModelSerializer.Meta.extra_kwargs | {
            'image': {'write_only': True},
        }


class VideoSerializer(MediaModelSerializer):
    """Serializer for videos."""

    class Meta(MediaModelSerializer.Meta):
        model = Video
        fields = MediaModelSerializer.Meta.fields + ['url', 'embed_code', 'duration']
        extra_kwargs = MediaModelSerializer.Meta.extra_kwargs | {'url': {'allow_null': False}}
