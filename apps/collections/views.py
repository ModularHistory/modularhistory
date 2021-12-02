from django.db.models.query import QuerySet

from apps.admin.views import AutocompleteJsonView
from apps.collections.models import Collection


class CollectionSearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self) -> 'QuerySet[Collection]':
        """Return the filtered queryset."""
        if self.term:
            return Collection.objects.search(term=self.term, elastic=False)
        return Collection.objects.all()
