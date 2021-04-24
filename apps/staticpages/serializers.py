"""Serializers for the StaticPages app."""
import serpy


class StaticPageSerializer(serpy.Serializer):
    """Serializer for static pages."""

    title = serpy.Field()
    content = serpy.Field()
