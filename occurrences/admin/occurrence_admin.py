"""Admin classes for occurrences."""

from admin import ModelAdmin, admin_site
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
from search.admin import SearchableModelAdmin
from sources.admin import CitationsInline
from sources.admin.filters import HasMultipleCitationsFilter, HasSourceFilter
from topics.admin import RelatedTopicsInline
from topics.models.taggable_model import TopicFilter


class OccurrenceAdmin(SearchableModelAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence

    exclude = SearchableModelAdmin.exclude
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
        'date_string',
    ]
    list_filter = [
        'verified',
        HasDateFilter,
        HasQuotesFilter,
        EntityFilter,
        TopicFilter,
        LocationFilter,
        HasSourceFilter,
        HasMultipleCitationsFilter,
    ]
    list_per_page = 10
    ordering = ['date']
    readonly_fields = SearchableModelAdmin.readonly_fields
    search_fields = models.Occurrence.searchable_fields

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'


class OccurrenceChainAdmin(ModelAdmin):
    """Admin for occurrence chains."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
