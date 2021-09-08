from rest_framework.viewsets import ModelViewSet

class ExtendedModelViewSet(ModelViewSet):
    """A ModelViewSet which allows accessing objects by slug or primary key."""

    lookup_url_kwarg = 'pk_or_slug'
    
    def get_object(self):
        self.lookup_field = 'pk' if str(self.kwargs[self.lookup_url_kwarg]).isnumeric() else 'slug'
        return super().get_object()
