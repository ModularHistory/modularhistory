"""Serializers for the entities app."""

from apps.topics.models import Topic
from core.models.module import ModuleSerializerDrf


class TopicModelSerializer(ModuleSerializerDrf):
    """Serializer for topics."""

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of serialized topics."""
        return 'topics.topic'

    class Meta(ModuleSerializerDrf.Meta):
        model = Topic
        fields = ModuleSerializerDrf.Meta.fields + [
            'name',
            'aliases',
            'description',
            'path',
        ]
