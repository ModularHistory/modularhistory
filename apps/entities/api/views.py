from django.db.models import QuerySet
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from modularhistory.pagination import VariableSizePagination

from apps.entities.models import Entity
from apps.entities.serializers import EntitySerializer, EntityPartialDictSerializer


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer


class EntityListAPIView(ListAPIView):
    """API view for listing entities."""

    serializer_class = EntitySerializer
    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore


class EntityPartialAPIView(ListAPIView):
    """API view for listing client-selected attributes of entities.

    Desired attributes are specified with the `attributes` query
    parameter, and only these attributes are retrieved.
    The client can use the `page_size` parameter to guarantee all
    results are in a single response.
    """

    pagination_class = VariableSizePagination
    serializer_class = EntityPartialDictSerializer

    def get_queryset(self):
        attributes = self.request.query_params.getlist('attributes')
        if not attributes:
            return []

        return Entity.objects.values(*attributes)
