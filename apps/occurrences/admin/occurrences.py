"""Admin classes for occurrences."""

from apps.admin import admin_site
from apps.images.admin import AbstractImagesInline
from apps.occurrences import models
from apps.occurrences.admin.filters import (
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from apps.places.admin import AbstractLocationsInline
from apps.propositions.admin import TypedPropositionAdmin
from apps.sources.admin.citations import AbstractSourcesInline
from apps.sources.admin.filters import HasMultipleSourcesFilter, HasSourceFilter
from apps.topics.models.taggable_model import TopicFilter


class ImagesInline(AbstractImagesInline):
    """Inline admin for an occurrence's images."""

    model = models.Occurrence.images.through


class SourcesInline(AbstractSourcesInline):
    """Inline admin for sources."""

    model = models.NewOccurrence.sources.through


class LocationsInline(AbstractLocationsInline):
    """Inline admin for an occurrence's locations."""

    model = models.Occurrence.locations.through


class OccurrenceAdmin(TypedPropositionAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'
    inlines = TypedPropositionAdmin.inlines + [LocationsInline, ImagesInline]
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
