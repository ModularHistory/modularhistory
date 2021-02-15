"""Serializers for the entities app."""

from typing import TYPE_CHECKING

import serpy

from modularhistory.models.model import ModelSerializer

if TYPE_CHECKING:
    from apps.entities.models import Entity


class CategorySerializer(serpy.Serializer):
    """Serializer for Entity Categories."""

    name = serpy.Field()


class CategorizationSerializer(serpy.Serializer):
    """Serializer for Entity-Category relationship."""

    category = CategorySerializer()
    start_date = serpy.MethodField('get_serialized_start_date')
    end_date = serpy.MethodField('get_serialized_end_date')

    def get_serialized_start_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return instance.date.serialize() if instance.date else None

    def get_serialized_end_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return instance.end_date.serialize() if instance.end_date else None


class EntitySerializer(ModelSerializer):
    """Serializer for entities."""

    name = serpy.Field()
    unabbreviated_name = serpy.Field()
    aliases = serpy.Field()
    birth_date = serpy.MethodField('get_serialized_birth_date')
    death_date = serpy.MethodField('get_serialized_death_date')
    description = serpy.Field(attr='description.html', required=False)
    serialized_images = serpy.Field()
    categorizations = CategorizationSerializer(
        many=True, attr='categorizations.all', call=True
    )

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return f'entities.{instance.__class__.__name__.lower()}'

    def get_serialized_birth_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return instance.birth_date.serialize() if instance.birth_date else None

    def get_serialized_death_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return instance.death_date.serialize() if instance.death_date else None
