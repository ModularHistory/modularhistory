from typing import Optional

from rest_framework.viewsets import ModelViewSet


class ExtendedModelViewSet(ModelViewSet):
    """A ModelViewSet which allows accessing objects by slug or primary key."""

    lookup_url_kwarg = 'pk_or_slug'
    list_fields: Optional[list[str]] = ['model', 'slug']

    def get_object(self):
        self.lookup_field = (
            'pk' if str(self.kwargs[self.lookup_url_kwarg]).isnumeric() else 'slug'
        )
        return super().get_object()

    def get_serializer(self, *args, **kwargs):
        fields = self.list_fields if self.action == 'list' else None
        return super().get_serializer(*args, **kwargs, fields=fields)
