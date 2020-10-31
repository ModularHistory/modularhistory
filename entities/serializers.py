"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers


class EntitySerializer(serializers.Serializer):
    """Serializer for entities."""

    name = serializers.CharField()
