"""Admin classes for occurrences."""


from admin import ModelAdmin, SearchableModelAdmin, admin_site
from modularhistory.models.taggable_model import TopicFilter
from occurrences import models
from occurrences.admin.occurrence_filters import (
    EntityFilter,
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from occurrences.admin.occurrence_inlines import (
    ImagesInline,
    InvolvedEntitiesInline,
    LocationsInline,
    OccurrencesInline,
)
from quotes.admin.related_quotes_inline import RelatedQuotesInline
from sources.admin import CitationsInline
from topics.admin import RelatedTopicsInline


class OccurrenceAdmin(SearchableModelAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence
    inlines = [
        RelatedQuotesInline,
        InvolvedEntitiesInline,
        LocationsInline,
        ImagesInline,
        CitationsInline,
        RelatedTopicsInline,
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
        LocationFilter,
    ]
    ordering = ['date']
    readonly_fields = SearchableModelAdmin.readonly_fields
    search_fields = models.Occurrence.searchable_fields


class OccurrenceChainAdmin(ModelAdmin):
    """Admin for occurrence chains."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
