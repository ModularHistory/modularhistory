from apps.graph.types import ModuleType
from apps.topics.models.topic import Topic


class TopicType(ModuleType):
    """GraphQL type for the Topic model."""

    class Meta:
        model = Topic
        exclude = []

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to a topic's `model` attribute."""
        return 'topics.topic'
