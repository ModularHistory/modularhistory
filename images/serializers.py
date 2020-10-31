"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers


class ImageSerializer(serializers.Serializer):
    """Serializer for images."""

    pk = serializers.IntegerField()
    src_url = serializers.CharField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    caption_html = serializers.CharField()
    provider_string = serializers.CharField()
