"""Serializers for the entities app."""


import serpy

from apps.dates.fields import TimelinePositionField
from core.models.module import ModuleSerializer


class QuoteSerializer(ModuleSerializer):
    """Serializer for quotes."""

    bite = serpy.StrField()
    html = serpy.StrField()
    attributee_html = serpy.StrField()
    attributee_string = serpy.StrField()
    date_string = serpy.StrField()
    cached_images = serpy.Field()
    primary_image = serpy.Field()
    cached_citations = serpy.Field()
    timeline_position = TimelinePositionField(attr='date', required=False)
