from typing import TYPE_CHECKING, Tuple, Type

from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import path

from admin.model_admin import ModelAdmin
from entities.views import EntityCategorySearchView, EntitySearchView
from topics.views import TagSearchView

if TYPE_CHECKING:
    from modularhistory.models import SearchableModel


class SearchableModelAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: Type['SearchableModel']

    readonly_fields = ['pretty_computations']

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet, search_term: str
    ) -> Tuple[QuerySet, bool]:
        """Return source search results to the admin."""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            queryset = self.model.objects.search(
                query=search_term,
                suppress_unverified=False,
                suppress_hidden=False,
            )
        return queryset, use_distinct

    def get_urls(self):
        """Return URLs used by searchable model admins."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'tag_search/',
                self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                name='tag_search',
            ),
            path(
                'entity_search/',
                self.admin_site.admin_view(EntitySearchView.as_view(model_admin=self)),
                name='entity_search',
            ),
            path(
                'entity_category_search/',
                self.admin_site.admin_view(
                    EntityCategorySearchView.as_view(model_admin=self)
                ),
                name='entity_category_search',
            ),
        ]
        return custom_urls + urls
