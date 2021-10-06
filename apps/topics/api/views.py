from apps.topics.api.serializers import TopicDrfSerializer
from apps.topics.models.topic import Topic
from core.api.views import ExtendedModelViewSet
from core.pagination import VariableSizePagination


class TopicViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing topics."""

    queryset = Topic.objects.all()
    serializer_class = TopicDrfSerializer
    pagination_class = VariableSizePagination
