from typing import Optional

from django.db.models import QuerySet
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet


class ExtendedModelViewSet(ModelViewSet):
    """A ModelViewSet which allows accessing objects by slug or primary key."""

    lookup_url_kwarg = 'pk_or_slug'
    list_fields: Optional[set[str]] = {'model', 'slug', 'title'}
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    prefetch_relations = []

    def get_object(self):
        is_slug = (
            'slug' in self.serializer_class.Meta.fields
            and not str(self.kwargs[self.lookup_url_kwarg]).isnumeric()
        )
        self.lookup_field = 'slug' if is_slug else 'pk'
        return super().get_object()

    def get_serializer(self, *args, **kwargs):
        fields = self.list_fields if self.action == 'list' else None
        return super().get_serializer(*args, **kwargs, fields=fields)

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.prefetch_related(*self.prefetch_relations)
