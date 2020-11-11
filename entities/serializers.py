"""Serializers for the entities app."""

from modularhistory.models.model import ModelSerializer
import serpy


class EntitySerializer(ModelSerializer):
    """Serializer for entities."""

    name = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return f'entities.{instance.__class__.__name__.lower()}'
