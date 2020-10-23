from admin import TabularInline
from occurrences import models


class LocationsInline(TabularInline):
    """Inline admin for an occurrence's locations."""

    model = models.Occurrence.locations.through
    extra = 1
    autocomplete_fields = ['location']


class ImagesInline(TabularInline):
    """Inline admin for an occurrence's images."""

    model = models.Occurrence.images.through
    extra = 0
    autocomplete_fields = ['image']
    readonly_fields = ['key', 'image_pk']


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
