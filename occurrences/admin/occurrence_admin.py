"""Admin classes for occurrences."""

from django.urls import path

from admin.model_admin import ModelAdmin, SearchableModelAdmin, admin_site
from modularhistory.models.taggable_model import TopicFilter
from occurrences import models
from occurrences.admin.occurrence_filters import EntityFilter, HasDateFilter, HasQuotesFilter, LocationFilter
from occurrences.admin.occurrence_inlines import (
    ImagesInline,
    InvolvedEntitiesInline,
    LocationsInline,
    OccurrencesInline
)
from quotes.admin import RelatedQuotesInline
from sources.admin import CitationsInline
from topics.admin import RelatedTopicsInline
from topics.views import TagSearchView


class OccurrenceAdmin(SearchableModelAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence
    inlines = [
        RelatedQuotesInline,
        InvolvedEntitiesInline,
        LocationsInline,
        ImagesInline,
        CitationsInline,
        RelatedTopicsInline
    ]
    list_display = [
        'pk',
        'summary',
        'detail_link',
        'truncated_description',
        'date_string',
    ]
    list_filter = [
        'verified',
        HasDateFilter,
        HasQuotesFilter,
        EntityFilter,
        TopicFilter,
        LocationFilter
    ]
    ordering = ['date']
    readonly_fields = ['computations']
    search_fields = models.Occurrence.searchable_fields

    def get_urls(self):
        """TODO: add docstring."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'tag_search/',
                self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                name='tag_search'
            ),
        ]
        return custom_urls + urls


class OccurrenceChainAdmin(ModelAdmin):
    """TODO: add docstring."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
