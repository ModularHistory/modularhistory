from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.collections.api.serializers import CollectionSerializer
from apps.collections.models import Collection


class CollectionViewSet(ModelViewSet):
    """API endpoint for viewing and editing collections."""

    queryset = Collection.objects.all()
    lookup_field = 'slug'
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
