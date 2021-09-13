"""Serializers for the entities app."""

from apps.topics.models import Topic
from core.models.module import DrfModuleSerializer


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
