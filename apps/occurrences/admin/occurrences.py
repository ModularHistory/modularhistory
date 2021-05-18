"""Admin classes for occurrences."""

from apps.admin import ModelAdmin, admin_site
from apps.entities.admin.inlines import AbstractRelatedEntitiesInline
from apps.occurrences import models
from apps.occurrences.admin.filters import (
    EntityFilter,
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from apps.occurrences.admin.inlines import (  # PostulationsInline,
    ImagesInline,
    InvolvedEntitiesInline,
    OccurrencesInline,
)
from apps.places.admin import AbstractLocationsInline
from apps.propositions.admin import PropositionChildAdmin
from apps.propositions.models.proposition import Proposition
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.citations import AbstractSourcesInline
from apps.sources.admin.filters import HasMultipleCitationsFilter, HasSourceFilter
from apps.topics.models.taggable_model import TopicFilter


class SourcesInline(AbstractSourcesInline):
    """Inline admin for sources."""

    model = models.NewOccurrence.sources.through


class RelatedEntitiesInline(AbstractRelatedEntitiesInline):
    """Inline admin for sources."""

    model = models.NewOccurrence.related_entities.through


class LocationsInline(AbstractLocationsInline):
    """Inline admin for an occurrence's locations."""

    model = models.NewOccurrence.locations.through


class NewOccurrenceAdmin(PropositionChildAdmin):
    """Model admin for occurrences."""

    base_model = Proposition
    model = models.NewOccurrence

    exclude = PropositionChildAdmin.exclude + [
        # Use inlines for m2m relations.
        'postulations',
        'images',
        'locations',
    ]
    inlines = PropositionChildAdmin.inlines + [
        LocationsInline,
        ImagesInline,
        # The following are included by PropositionChildAdmin:
        #   RelatedQuotesInline,
        #   RelatedEntitiesInline,
        #   SourcesInline,
    ]
    list_display = [
        'slug',
        'title',
        'summary',
        'date_string',
        'tags_string',
    ]
    list_editable = ['title']
    list_filter = [
        'verified',
        HasDateFilter,
        HasQuotesFilter,
        TopicFilter,
        LocationFilter,
        HasSourceFilter,
        HasMultipleCitationsFilter,
        # HasMultipleImagesFilter,
    ]
    list_per_page = 10
    ordering = ['date']
    readonly_fields = SearchableModelAdmin.readonly_fields
    search_fields = model.searchable_fields

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'


class OccurrenceAdmin(SearchableModelAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence

    exclude = SearchableModelAdmin.exclude + ['postulations']
    inlines = [
        # RelatedQuotesInline,
        InvolvedEntitiesInline,
        # LocationsInline,
        # CitationsInline,
    ]
    list_display = [
        'pk',
        'slug',
        'title',
        'summary',
        # 'detail_link',
        'date_string',
        'tags_string',
    ]
    list_editable = ['title']
    list_filter = [
        'verified',
        HasDateFilter,
        # HasQuotesFilter,
        EntityFilter,
        TopicFilter,
        # LocationFilter,
        # HasSourceFilter,
        # HasMultipleCitationsFilter,
    ]
    list_per_page = 10
    ordering = ['date', 'pk']
    readonly_fields = SearchableModelAdmin.readonly_fields
    search_fields = model.searchable_fields

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'


class OccurrenceChainAdmin(ModelAdmin):
    """Admin for occurrence chains."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.NewOccurrence, NewOccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
