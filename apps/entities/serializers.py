"""Serializers for the entities app."""

import serpy

from modularhistory.models.model import ModelSerializer


class CategorySerializer(serpy.Serializer):
    """Serializer for Entity Categories."""

    name = serpy.Field()


class CategorizationSerializer(serpy.Serializer):
    """Serializer for Entity-Category relationship."""

    category = CategorySerializer()
    start_date = serpy.Field(attr='date')
    end_date = serpy.Field()


class EntitySerializer(ModelSerializer):
    """Serializer for entities."""

    name = serpy.Field()
    unabbreviated_name = serpy.Field()
    aliases = serpy.Field()
    birth_date = serpy.Field()
    death_date = serpy.Field()
    description = serpy.Field(attr='description.html', required=False)
    serialized_images = serpy.Field()
    categorizations = CategorizationSerializer(
        many=True, attr='categorizations.all', call=True
    )

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return f'entities.{instance.__class__.__name__.lower()}'
