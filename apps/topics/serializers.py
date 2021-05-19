"""Serializers for the entities app."""

import serpy

from core.models.model import ModelSerializer


class TopicSerializer(ModelSerializer):
    """Serializer for topics."""

    name = serpy.Field()
    key = serpy.StrField()
    aliases = serpy.StrField()
    description = serpy.MethodField('get_description')
    path = serpy.StrField()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of serialized topics."""
        return 'topics.topic'

    def get_description(self, instance) -> str:
        return instance.description.raw_value if instance.description else ''


class TopicDictSerializer:
    """Serializer for topics retrieved from ORM with `.values()`."""

    def __init__(self, queryset, *args, **kwargs):
        self.data = list(queryset)
