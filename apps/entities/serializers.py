"""Serializers for the entities app."""

import serpy

from modularhistory.models.model import ModelSerializer


class EntitySerializer(ModelSerializer):
    """Serializer for entities."""

    name = serpy.Field()
    unabbreviated_name = serpy.Field()
    aliases = serpy.Field()
    birth_date = serpy.Field()
    death_date = serpy.Field()
    description = serpy.MethodField()
    serialized_images = serpy.Field()

    def get_description(self, instance) -> str:
        return instance.description.html

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return f'entities.{instance.__class__.__name__.lower()}'
