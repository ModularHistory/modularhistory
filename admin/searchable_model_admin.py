from typing import TYPE_CHECKING, Tuple, Type

from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from admin.model_admin import ModelAdmin

if TYPE_CHECKING:
    from modularhistory.models import SearchableModel


class SearchableModelAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: Type['SearchableModel']

    readonly_fields = ['computations']

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet, search_term: str
    ) -> Tuple[QuerySet, bool]:
        """Custom implementation for searching sources in the admin."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            print(f'Django admin search function returned queryset: {queryset}')
            print(f'Falling back on sources.manager.search with query={search_term}...')
            queryset = self.model.objects.search(search_term, suppress_unverified=False)
        return queryset, use_distinct
