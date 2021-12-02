from apps.sources.api.sources.entry.serializers import EntrySerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Entry


class EntryViewSet(SourceViewSet):
    """API endpoint for viewing and editing journal entry sources."""

    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
