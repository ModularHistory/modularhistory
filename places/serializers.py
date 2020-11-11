"""Serializers for the entities app."""


import serpy
from modularhistory.models.model import ModelSerializer


class PlaceSerializer(ModelSerializer):
    """Serializer for places."""

    string = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return f'places.place'
