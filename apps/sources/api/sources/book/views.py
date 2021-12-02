from apps.sources.api.sources.book.serializers import BookSerializer, SectionSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Book, Section


class BookViewSet(SourceViewSet):
    """API endpoint for viewing and editing book sources."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer


class SectionViewSet(SourceViewSet):
    """API endpoint for viewing and editing book section sources."""

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
