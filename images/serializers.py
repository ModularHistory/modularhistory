"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers

from images.models import Image


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for images."""

    class Meta:
        model = Image
        fields = [
            'image',
            'links',
            'width',
            'height',
        ]
