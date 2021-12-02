"""Serializers for the entities app."""

from apps.topics.models import Topic
from core.models.serializers import DrfModuleSerializer


class TopicSerializer(DrfModuleSerializer):
    """Serializer for topics."""

    class Meta(DrfModuleSerializer.Meta):
        model = Topic
        fields = DrfModuleSerializer.Meta.fields + [
            'name',
            'aliases',
            'description',
        ]
        fields.remove('tags')
