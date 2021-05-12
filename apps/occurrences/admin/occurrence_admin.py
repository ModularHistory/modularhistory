"""Admin classes for occurrences."""

from apps.admin import ModelAdmin, admin_site
from apps.occurrences import models
from apps.occurrences.admin.occurrence_filters import (
    EntityFilter,
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from apps.occurrences.admin.occurrence_inlines import (
    ImagesInline,
    InvolvedEntitiesInline,
    LocationsInline,
    OccurrencesInline,
    PostulationsInline,
)
from apps.quotes.admin.related_quotes_inline import RelatedQuotesInline
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin import CitationsInline
from apps.sources.admin.filters import HasMultipleCitationsFilter, HasSourceFilter
from apps.topics.admin import RelatedTopicsInline
from apps.topics.models.taggable_model import TopicFilter


class OccurrenceAdmin(SearchableModelAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence

    exclude = SearchableModelAdmin.exclude + ['postulations']
    inlines = [
        PostulationsInline,
        RelatedQuotesInline,
        InvolvedEntitiesInline,
        LocationsInline,
        ImagesInline,
        CitationsInline,
        RelatedTopicsInline,
    ]
    list_display = [
        'pk',
        'title',
        'summary',
        # 'detail_link',
        'date_string',
        'slug',
    ]
    list_editable = ['title', 'slug']
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
    search_fields = model.searchable_fields

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'


class OccurrenceChainAdmin(ModelAdmin):
    """Admin for occurrence chains."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
