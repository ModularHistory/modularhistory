from typing import TYPE_CHECKING

from rest_framework import serializers

from apps.search.api.serializers import DrfSearchableModelSerializer
from apps.topics.models import Topic

from .model import validate_model_type

if TYPE_CHECKING:
    from .module import Module


class DrfModuleSerializer(DrfSearchableModelSerializer):
    """Base serializer for ModularHistory's modules."""

    id = serializers.ReadOnlyField()
    model = serializers.SerializerMethodField()

    title = serializers.CharField(required=False, allow_blank=True)
    slug = serializers.CharField(required=False)
    absolute_url = serializers.CharField(required=False)
    admin_url = serializers.CharField(required=False)
    cached_tags = serializers.JSONField(required=False)

    class Meta(DrfSearchableModelSerializer.Meta):
        model: type['Module']
        fields = [
            'id',
            'model',
            'title',
            'slug',
            'absolute_url',
            'admin_url',
            'tags',
            'cached_tags',
        ] + DrfSearchableModelSerializer.Meta.fields
        extra_kwargs = {
            'tags': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Topic.objects.all(),
            }
        }


class DrfTypedModuleSerializer(DrfModuleSerializer):
    """Base serializer for ModularHistory's typed modules."""

    type = serializers.CharField(required=True)

    def validate_type(self, value):
        return validate_model_type(self, value)

    class Meta(DrfModuleSerializer.Meta):
        fields = DrfModuleSerializer.Meta.fields + ['type']


class SerializableDrfField(serializers.Field):
    """DRF field serializer that uses models .serialize() which uses Model.serializer_class"""

    def to_representation(self, value):
        return value.serialize()
