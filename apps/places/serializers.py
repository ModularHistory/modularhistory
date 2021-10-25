"""Serializers for the entities app."""


import serpy

from core.models.model import ModelSerializer


class PlaceSerializer(ModelSerializer):
    """Serializer for places."""

    string = serpy.Field()
