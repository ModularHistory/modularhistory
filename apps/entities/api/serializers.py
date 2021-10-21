from rest_framework import serializers

from apps.dates.fields import HistoricDateTimeDrfField
from apps.dates.structures import serialize_date
from apps.entities.models.entity import Entity
from core.models.serializers import DrfTypedModuleSerializer


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

    # write only versions are not rendered to output
    birth_date = HistoricDateTimeDrfField(write_only=True, required=False)
    death_date = HistoricDateTimeDrfField(write_only=True, required=False)
    birth_date_serialized = serializers.SerializerMethodField(
        'get_serialized_birth_date', read_only=True
    )
    death_date_serialized = serializers.SerializerMethodField(
        'get_serialized_death_date', read_only=True
    )

    def get_serialized_birth_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return serialize_date(instance.birth_date)

    def get_serialized_death_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return serialize_date(instance.death_date)

    class Meta(DrfTypedModuleSerializer.Meta):
        model = Entity
        read_only_fields = ['truncated_description']
        fields = DrfTypedModuleSerializer.Meta.fields + [
            'name',
            'unabbreviated_name',
            'aliases',
            'description',
            'truncated_description',
            'categorizations',
            'birth_date',
            'death_date',
            'birth_date_serialized',
            'death_date_serialized',
            'primary_image',
        ]
