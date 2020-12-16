"""Serializers for the entities app."""

import serpy

from modularhistory.models.model import ModelSerializer


class EntitySerializer(ModelSerializer):
    """Serializer for entities."""

    name = serpy.Field()
    serialized_images = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return f'entities.{instance.__class__.__name__.lower()}'
