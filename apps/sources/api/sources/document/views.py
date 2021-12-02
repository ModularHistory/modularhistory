from django.db.models import Prefetch

from apps.places.models import Place
from apps.sources.api.sources.document.serializers import DocumentSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Collection, Document, Repository

document_prefetch = Prefetch(
    'collection',
    queryset=Collection.objects.all().prefetch_related(
        Prefetch(
            'repository',
            queryset=Repository.objects.all().prefetch_related(
                Prefetch('location', queryset=Place.objects.all())
            ),
        )
    ),
)


class DocumentViewSet(SourceViewSet):
    """API endpoint for viewing and editing document sources."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    prefetch_relations = SourceViewSet.prefetch_relations + [
        document_prefetch,
        Prefetch(
            'original_edition',
            queryset=Document.objects.all().prefetch_related('tags', document_prefetch),
        ),
    ]
