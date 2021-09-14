"""Serializers for the entities app."""
from rest_framework import serializers

from apps.topics.models import Topic
from core.models.module import DrfModuleSerializer


class TaggableDrfModuleSerializer(DrfModuleSerializer):
    """Serializer for taggable modules.
    TODO: merge this with parent serializer after moving parent to be able to import Topic model without circular imports
    """

    cached_tags = serializers.JSONField(required=False)

    class Meta(DrfModuleSerializer.Meta):
        fields = DrfModuleSerializer.Meta.fields + ['cached_tags', 'tags']
        extra_kwargs = {
            'tags': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Topic.objects.all(),
            }
        }


class TopicDrfSerializer(DrfModuleSerializer):
    """Serializer for topics."""

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of serialized topics."""
        return 'topics.topic'

    class Meta(DrfModuleSerializer.Meta):
        model = Topic
        fields = DrfModuleSerializer.Meta.fields + [
            'name',
            'aliases',
            'description',
        ]
