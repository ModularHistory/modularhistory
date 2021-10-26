"""Serializers for the FlatPages app."""
import serpy


class FlatPageSerializer(serpy.Serializer):
    """Serializer for static pages."""

    title = serpy.StrField()
    content = serpy.StrField()
    path = serpy.StrField()
