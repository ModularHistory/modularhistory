from apps.sources.api.sources.report.serializers import ReportSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Report


class ReportViewSet(SourceViewSet):
    """API endpoint for viewing and editing report sources."""

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
