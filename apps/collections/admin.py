from django.contrib.admin.options import TabularInline
from django.urls import reverse

from apps.admin.list_filters.autocomplete_filter import ManyToManyAutocompleteFilter
from apps.admin.model_admin import admin_site
from apps.collections import models
from apps.search.admin import SearchableModelAdmin
from apps.topics.models.taggable_model import TopicFilter


class CollectionAdmin(SearchableModelAdmin):
    """Admin for collections."""

    model = models.Collection

    list_display = ['slug', 'title', 'creator']
    list_filter = [TopicFilter, 'creator']
    search_fields = model.searchable_fields


class CollectionsInline(TabularInline):
    """Inline admin for collections."""

    model = models.Collection


class CollectionFilter(ManyToManyAutocompleteFilter):
    """Filter for model instances included in a collection."""

    title = 'collections'
    field_name = 'collections'
    _parameter_name = 'collections__pk__exact'
    m2m_cls = models.Collection

    def get_autocomplete_url(self, request, model_admin):
        """Return the URL used for topic autocompletion."""
        return reverse('admin:collection_search')


admin_site.register(models.Collection, CollectionAdmin)
