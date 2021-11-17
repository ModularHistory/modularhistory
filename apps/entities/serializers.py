"""Serializers for the entities app."""

from typing import TYPE_CHECKING

import serpy

from apps.dates.fields import TimelinePositionField
from core.models.module import ModuleSerializer

if TYPE_CHECKING:
    from apps.entities.models.entity import Entity


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


class EntitySerializer(ModuleSerializer):
    """Serializer for entities."""

    name = serpy.StrField()
    unabbreviated_name = serpy.StrField()
    aliases = serpy.Field()
    birth_date = serpy.MethodField('get_serialized_birth_date')
    death_date = serpy.MethodField('get_serialized_death_date')
    description = serpy.StrField(required=False)
    truncated_description = serpy.StrField()
    cached_images = serpy.Field()
    categorizations = CategorizationSerializer(
        many=True, attr='categorizations.all', call=True
    )
    timeline_position = TimelinePositionField(attr='birth_date', required=False)

    def get_serialized_birth_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return instance.birth_date.serialize() if instance.birth_date else None

    def get_serialized_death_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return instance.death_date.serialize() if instance.death_date else None
