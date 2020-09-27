from django.urls import path

from admin.admin import admin_site, Admin
from history.models.taggable_model import TopicFilter
from occurrences import models
from occurrences.admin.occurrence_filters import EntityFilter, HasDateFilter, HasQuotesFilter, LocationFilter
from occurrences.admin.occurrence_inlines import (
    OccurrencesInline,
    InvolvedEntitiesInline,
    LocationsInline,
    ImagesInline
)
from quotes.admin import RelatedQuotesInline
from sources.admin import CitationsInline
from topics.admin import RelatedTopicsInline
from topics.views import TagSearchView


class OccurrenceAdmin(Admin):
    """TODO: add docstring."""

    base_model = models.Occurrence
    list_display = [
        'pk',
        'summary',
        'detail_link',
        'truncated_description',
        'date_string',
        # 'tags_string'
    ]
    list_filter = [
        'verified',
        HasDateFilter,
        HasQuotesFilter,
        EntityFilter,
        TopicFilter,
        LocationFilter
    ]
    search_fields = models.Occurrence.searchable_fields
    ordering = ['date']
    inlines = [
        RelatedQuotesInline, InvolvedEntitiesInline,
        LocationsInline, ImagesInline,
        CitationsInline,
        RelatedTopicsInline
    ]

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


class OccurrenceChainAdmin(Admin):
    """TODO: add docstring."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
