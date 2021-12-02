"""Serializers for the entities app."""

from apps.topics.models import Topic
from core.models.serializers import ModuleSerializer


class TopicSerializer(ModuleSerializer):
    """Serializer for topics."""

    class Meta(ModuleSerializer.Meta):
        model = Topic
        fields = ModuleSerializer.Meta.fields + [
            'name',
            'aliases',
            'description',
        ]
        fields.remove('tags')
