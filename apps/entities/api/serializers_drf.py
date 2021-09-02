from rest_framework import serializers

from apps.entities.models.entity import Entity
from apps.search.api.serializers import SearchableModelSerializerDrf


class CategorySerializerDrf(serializers.Serializer):
    """Serializer for Entity Categories."""

    name = serializers.Field()


class CategorizationSerializerDrf(serializers.Serializer):
    """Serializer for Entity-Category relationship."""

    category = CategorySerializerDrf()
    start_date = serializers.SerializerMethodField('get_serialized_start_date')
    end_date = serializers.SerializerMethodField('get_serialized_end_date')

    def get_serialized_start_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return instance.date.serialize() if instance.date else None

    def get_serialized_end_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return instance.end_date.serialize() if instance.end_date else None


class EntitySerializerDrf(SearchableModelSerializerDrf):
    """Serializer for entities."""
    description = serializers.CharField(required=False)
    birthdate = serializers.DateField(write_only=True)
    deathdate = serializers.DateField(write_only=True)
    birth_date = serializers.SerializerMethodField('get_serialized_birth_date', read_only=True)
    death_date = serializers.SerializerMethodField('get_serialized_death_date', read_only=True)

    # categorizations = CategorizationSerializerDrf(
    #     many=True, attr='categorizations.all', call=True
    # )

    def get_serialized_birth_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return instance.birth_date.serialize() if instance.birth_date else None

    def get_serialized_death_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return instance.death_date.serialize() if instance.death_date else None

    class Meta:
        model = Entity
        fields = ['type', 'name', 'unabbreviated_name', 'aliases', 'description', 'truncated_description',
                  'birthdate', 'deathdate', 'birth_date', 'death_date']
        read_only_fields = ['truncated_description']
