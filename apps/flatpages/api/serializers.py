"""Serializers for the FlatPages app."""

from rest_framework.serializers import ModelSerializer
from apps.flatpages.models import FlatPage


class FlatPageSerializer(serpy.Serializer):
    """Serializer for static pages."""

    class Meta:
        model = FlatPage

    title = serpy.StrField()
    meta_description = serpy.StrField()
    content = serpy.StrField()  # noqa: WPS110
    path = serpy.StrField()
