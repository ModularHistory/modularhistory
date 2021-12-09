from typing import Optional

from django.db.models import Prefetch, QuerySet
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.pagination import VariableSizePagination


class ExtendedModelViewSet(ModelViewSet):
    """A ModelViewSet which allows accessing objects by slug or primary key."""

    lookup_url_kwarg = 'pk_or_slug'
    list_fields: Optional[set[str]] = {'model', 'slug', 'title'}
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    prefetch_relations = []

    pagination_class = VariableSizePagination

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
        prefetch_relations = self.prefetch_relations
        # remove simple prefetches if Prefetch object with same name exists
        # allows to override parent class declared prefetch relations and avoid duplicates
        for prefetch in prefetch_relations:
            if isinstance(prefetch, Prefetch):
                name = prefetch.prefetch_through
                if name in prefetch_relations:
                    prefetch_relations.remove(name)
        return queryset.prefetch_related(*prefetch_relations)

    moderated_fields_lookup_keyword = 'fields'

    def retrieve(self, request, *args, **kwargs):
        is_moderated_fields = (
            self.kwargs[self.lookup_url_kwarg] == self.moderated_fields_lookup_keyword
        )
        if is_moderated_fields:
            serializer = self.get_serializer()
            return Response(serializer.get_moderated_fields())
        else:
            return super().retrieve(request, *args, **kwargs)

    def create(self, *args, **kwargs):
        response = super().create(*args, **kwargs)
        from pprint import pprint

        pprint(response.__dict__)
        try:
            print(response)
            response.data['change_id'] = 1
        except Exception as e:
            print('\n' * 10)
            print(e)
        return response
