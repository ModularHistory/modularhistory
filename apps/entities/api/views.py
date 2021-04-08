from django.db.models import QuerySet
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination

from apps.entities.models import Entity
from apps.entities.serializers import EntitySerializer, EntityPartialDictSerializer


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class EntityListAPIView(ListAPIView):
    """API view for listing entities."""

    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if len(self.request.query_params) == 0:
            return EntitySerializer
        return EntityPartialDictSerializer

    def get_queryset(self):
        attributes = self.request.query_params.getlist('attributes')

        if attributes:
            queryset = Entity.objects.values(*attributes)
            # TODO: support dynamic page size in query parameter
            self.pagination_class = LargePagePagination
        else:
            queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
            self.pagination_class = PageNumberPagination
        return queryset


class LargePagePagination(PageNumberPagination):
    page_size = 1000
