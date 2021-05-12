from typing import TYPE_CHECKING, Tuple, Type

from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import path

from apps.admin.model_admin import ModelAdmin, admin_site
from apps.entities.views import EntityCategorySearchView, EntitySearchView
from apps.search import models
from apps.topics.views import TagSearchView

if TYPE_CHECKING:
    from apps.search.models import SearchableModel


class SearchableModelAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: Type['SearchableModel']

    exclude = ['computations']
    readonly_fields = ['pretty_computations']

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the admin."""
        fields = super().get_fields(request, model_instance)
        ordered_field_names = ('notes',)
        for field_name in ordered_field_names:
            if field_name in fields:
                fields.remove(field_name)
                fields.insert(0, field_name)
        return fields

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
        # TODO: Use ElasticSearch in the admin.
        # This is a workaround for a bug that's causing duplicate results.
        # return queryset, use_distinct
        return (
            self.model.objects.filter(id__in={instance.id for instance in queryset}),
            use_distinct,
        )

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


class SearchAdmin(ModelAdmin):
    """Admin for user searches."""

    list_display = ['pk']


admin_site.register(models.Search, SearchAdmin)
