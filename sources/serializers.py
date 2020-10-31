"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers


class SourceSerializer(serializers.Serializer):
    """Serializer for sources."""

    html = serializers.CharField(source='html')


class CitationSerializer(serializers.Serializer):
    """Serializer for citations."""

    html = serializers.CharField()
    pk = serializers.IntegerField()
