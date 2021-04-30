from apps.graph.types import ModuleType
from apps.topics.models.topic import Topic


class TopicType(ModuleType):
    """GraphQL type for the Topic model."""

    class Meta:
        model = Topic
        exclude = ['related']

    def resolve_model(self, *args) -> str:
        return 'topics.topic'
