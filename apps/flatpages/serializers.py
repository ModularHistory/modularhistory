"""Serializers for the FlatPages app."""
import serpy


class FlatPageSerializer(serpy.Serializer):
    """Serializer for static pages."""

    title = serpy.Field()
    content = serpy.Field()
    path = serpy.Field()
