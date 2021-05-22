"""Admin classes for occurrences."""

from apps.admin.admin_site import admin_site
from apps.occurrences import models
from apps.occurrences.admin.filters import (
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from apps.places.admin import AbstractLocationsInline
from apps.propositions.admin import TypedPropositionAdmin
from apps.sources.admin.filters import HasMultipleSourcesFilter, HasSourceFilter
from apps.topics.models.taggable_model import TopicFilter


class LocationsInline(AbstractLocationsInline):
    """Inline admin for an occurrence's locations."""

    model = models.Occurrence.locations.through


class OccurrenceAdmin(TypedPropositionAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence

    inlines = TypedPropositionAdmin.inlines + [LocationsInline]
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
        HasMultipleSourcesFilter,
        # HasMultipleImagesFilter,
    ]
    ordering = ['date']


admin_site.register(models.Occurrence, OccurrenceAdmin)
# admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
