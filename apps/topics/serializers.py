"""Serializers for the entities app."""

import serpy

from core.models.module import ModuleSerializer


class TopicSerializer(ModuleSerializer):
    """Serializer for topics."""

    name = serpy.StrField()
    aliases = serpy.StrField()
    description = serpy.StrField()
    path = serpy.StrField()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of serialized topics."""
        return 'topics.topic'


class TopicDictSerializer:
    """Serializer for topics retrieved from ORM with `.values()`."""

    def __init__(self, queryset, *args, **kwargs):
        """Construct the serializer."""
        self.data = list(queryset)
