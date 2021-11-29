"""Serializers for the entities app."""

import serpy

from apps.dates.fields import TimelinePositionField
from core.models.module import ModuleSerializer


class ImageSerializer(ModuleSerializer):
    """Serializer for images."""

    src_url = serpy.StrField()
    width = serpy.IntField()
    height = serpy.IntField()
    caption_html = serpy.StrField()
    provider_string = serpy.StrField()
    bg_img_position = serpy.Field()
    timeline_position = TimelinePositionField(attr='date', required=False)
