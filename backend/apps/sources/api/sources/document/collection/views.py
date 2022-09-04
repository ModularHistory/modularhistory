from apps.sources.api.sources.document.collection.serializers import (
    CollectionSerializer,
    RepositorySerializer,
)
from apps.sources.models import Collection, Repository
from core.api.views import ExtendedModelViewSet


class RepositoryViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing source document collection repositories."""

    list_fields = None
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer


class CollectionViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing source document collections."""

    list_fields = None
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
