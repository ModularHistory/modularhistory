from rest_framework import serializers

from apps.dates.api.fields import HistoricDateTimeField, TimelinePositionField
from apps.dates.structures import serialize_date
from apps.entities.models.entity import Entity
from apps.images.models import Image
from core.models.serializers import TypedModuleSerializer


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


class EntitySerializer(TypedModuleSerializer):
    """Serializer for entities.
    TODO: need to validate birth/date is correctly typed occurrence (propositions.Birth/Death) and need to serialize if needed
    """

    description = serializers.CharField(required=False)
    categorizations = CategorizationSerializer(
        many=True, required=False, source='categorizations.all'
    )

    # write only versions are not rendered to output
    birth_date = HistoricDateTimeField(write_only=True, required=False)
    death_date = HistoricDateTimeField(write_only=True, required=False)
    birth_date_serialized = serializers.SerializerMethodField(
        'get_serialized_birth_date', read_only=True
    )
    death_date_serialized = serializers.SerializerMethodField(
        'get_serialized_death_date', read_only=True
    )
    timeline_position = TimelinePositionField(
        read_only=True, required=False, source='birth_date'
    )

    def get_serialized_birth_date(self, instance: 'Entity'):
        """Return the entity's birth date, serialized."""
        return serialize_date(instance.birth_date)

    def get_serialized_death_date(self, instance: 'Entity'):
        """Return the entity's death date, serialized."""
        return serialize_date(instance.death_date)

    class Meta(TypedModuleSerializer.Meta):
        model = Entity
        read_only_fields = ['truncated_description']
        fields = TypedModuleSerializer.Meta.fields + [
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
            'birth',
            'death',
            'images',
            'cached_images',
            'primary_image',
            'reference_urls',
            'timeline_position',
        ]
        extra_kwargs = TypedModuleSerializer.Meta.extra_kwargs | {
            'images': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Image.objects.all(),
            },
        }
