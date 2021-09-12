from typing import Optional
from rest_framework.viewsets import ModelViewSet


class ExtendedModelViewSet(ModelViewSet):
    """A ModelViewSet which allows accessing objects by slug or primary key."""

    lookup_url_kwarg = 'pk_or_slug'
    list_attributes: Optional[list[str]] = None

    def get_object(self):
        self.lookup_field = (
            'pk' if str(self.kwargs[self.lookup_url_kwarg]).isnumeric() else 'slug'
        )
        return super().get_object()

    def list(self, *args, **kwargs):
        if self.list_attributes is not None:
            self.queryset = self.queryset.values(*self.list_attributes)
        return super().list(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs, fields=self.list_attributes)
