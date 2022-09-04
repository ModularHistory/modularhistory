"""Serializers for the entities app."""


class TopicDictSerializer:
    """Serializer for topics retrieved from ORM with `.values()`."""

    def __init__(self, queryset, *args, **kwargs):
        """Construct the serializer."""
        self.data = list(queryset)
