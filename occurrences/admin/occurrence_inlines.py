from admin.admin import TabularInline
from occurrences import models


class LocationsInline(TabularInline):
    """TODO: add docstring."""

    model = models.Occurrence.locations.through
    extra = 1
    autocomplete_fields = ['location']


class ImagesInline(TabularInline):
    """TODO: add docstring."""

    model = models.Occurrence.images.through
    extra = 0
    autocomplete_fields = ['image']
    readonly_fields = ['key', 'image_pk']


class InvolvedEntitiesInline(TabularInline):
    """TODO: add docstring."""

    model = models.Occurrence.involved_entities.through
    extra = 1
    autocomplete_fields = ['entity']


class OccurrencesInline(TabularInline):
    """TODO: add docstring."""

    model = models.Occurrence.chains.through
    autocomplete_fields = ['occurrence']
    extra = 1
