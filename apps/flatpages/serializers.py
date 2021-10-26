"""Serializers for the FlatPages app."""
import serpy


class FlatPageSerializer(serpy.Serializer):
    """Serializer for static pages."""

    title = serpy.StrField()
    meta_description = serpy.StrField()
    content = serpy.StrField()  # noqa: WPS110
    path = serpy.StrField()
