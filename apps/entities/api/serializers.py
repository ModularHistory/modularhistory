from rest_framework import serializers

from apps.entities.models.entity import Entity
from core.models.module import ModuleSerializerDrf


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


class EntityModelSerializer(ModuleSerializerDrf):
    """Serializer for entities."""

    description = serializers.CharField(required=False)
    categorizations = CategorizationSerializer(
        many=True, required=False, source='categorizations.all'
    )

    birth_date = serializers.DateField(write_only=True, required=False)
    death_date = serializers.DateField(write_only=True, required=False)
    birthDate = serializers.SerializerMethodField('get_serialized_birth_date', read_only=True)
    deathDate = serializers.SerializerMethodField('get_serialized_death_date', read_only=True)

    def get_serialized_birth_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return instance.birth_date.serialize() if instance.birth_date else None

    def get_serialized_death_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return instance.death_date.serialize() if instance.death_date else None

    class Meta(ModuleSerializerDrf.Meta):
        model = Entity
        fields = ModuleSerializerDrf.Meta.fields + [
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
