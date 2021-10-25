from apps.sources.api.sources.interview.serializers import InterviewDrfSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Interview


class InterviewViewSet(SourceViewSet):
    """API endpoint for viewing and editing interview sources."""

    queryset = Interview.objects.all()
    serializer_class = InterviewDrfSerializer
