import datetime

from rest_framework import serializers

from apps.dates.structures import HistoricDateTime
from apps.entities.models.entity import Entity
from core.models.module import DrfTypedModuleSerializer


class CategorySerializer(serializers.Serializer):
    """Serializer for Entity Categories."""

    name = serializers.ReadOnlyField()


class CategorizationSerializer(serializers.Serializer):
    """Serializer for Entity-Category relationship."""

    category = CategorySerializer()
    start_date = serializers.SerializerMethodField('get_serialized_start_date')
    end_date = serializers.SerializerMethodField('get_serialized_end_date')

    def get_serialized_start_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return instance.date.serialize() if instance.date else None

    def get_serialized_end_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return instance.end_date.serialize() if instance.end_date else None


class EntityDrfSerializer(DrfTypedModuleSerializer):
    """Serializer for entities."""

    description = serializers.CharField(required=False)
    categorizations = CategorizationSerializer(
        many=True, required=False, source='categorizations.all'
    )

    # write only fields are not rendered to output
    birth_date = serializers.DateTimeField(write_only=True, required=False)
    death_date = serializers.DateTimeField(write_only=True, required=False)
    birthDate = serializers.SerializerMethodField('get_serialized_birth_date', read_only=True)
    deathDate = serializers.SerializerMethodField('get_serialized_death_date', read_only=True)

    def get_serialized_birth_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        birth_date = instance.birth_date
        if isinstance(birth_date, HistoricDateTime):
            return birth_date.serialize()
        elif isinstance(birth_date, datetime.datetime):
            return birth_date.isoformat()
        else:
            return None

    def get_serialized_death_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        death_date = instance.death_date
        if isinstance(death_date, HistoricDateTime):
            return death_date.serialize()
        elif isinstance(death_date, datetime.datetime):
            return death_date.isoformat()
        else:
            return None

    class Meta(DrfTypedModuleSerializer.Meta):
        model = Entity
        fields = DrfTypedModuleSerializer.Meta.fields + [
            'name',
            'unabbreviated_name',
            'aliases',
            'description',
            'truncated_description',
            'categorizations',
            'birth_date',
            'death_date',
            'birthDate',
            'deathDate',
        ]
        read_only_fields = ['truncated_description']
