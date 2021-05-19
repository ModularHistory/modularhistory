from apps.admin import TabularInline
from apps.images.admin import AbstractImagesInline
from apps.occurrences import models


class LocationsInline(TabularInline):
    """Inline admin for an occurrence's locations."""

    model = models.Occurrence.locations.through
    extra = 1
    autocomplete_fields = ['place']
    verbose_name = 'location'
    verbose_name_plural = 'locations'


class ImagesInline(AbstractImagesInline):
    """Inline admin for an occurrence's images."""

    model = models.NewOccurrence.images.through
    readonly_fields = []


class InvolvedEntitiesInline(TabularInline):
    """Inline admin for an occurrence's involved entities."""

    model = models.Occurrence.involved_entities.through
    extra = 1
    autocomplete_fields = ['entity']


class OccurrencesInline(TabularInline):
    """Inline admin for an occurrence chain's occurrences."""  # right?

    model = models.Occurrence.chains.through
    autocomplete_fields = ['occurrence']
    extra = 1
