"""Serializers for the FlatPages app."""

from rest_framework.serializers import ModelSerializer

from apps.flatpages.models import FlatPage


class FlatPageSerializer(ModelSerializer):
    """Serializer for static pages."""

    class Meta:
        model = FlatPage
        fields = [
            'title',
            'meta_description',
            'content',
            'path',
        ]
