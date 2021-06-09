from typing import TYPE_CHECKING

from apps.admin.inlines import TabularInline
from apps.entities.admin.inlines import AbstractRelatedEntitiesInline
from apps.images.admin import AbstractImagesInline
from apps.places.admin import AbstractLocationsInline
from apps.propositions import models
from apps.sources.admin.citations import AbstractSourcesInline
from apps.topics.admin.tags import AbstractTagsInline

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest


class TagsInline(AbstractTagsInline):
    """Inline admin for topic tags."""

    model = models.Proposition.tags.through


class SourcesInline(AbstractSourcesInline):
    """Inline admin for sources."""

    model = models.Proposition.sources.through


class RelatedEntitiesInline(AbstractRelatedEntitiesInline):
    """Inline admin for related entities."""

    model = models.Proposition.related_entities.through


class ImagesInline(AbstractImagesInline):
    """Inline admin for images."""

    model = models.Proposition.images.through


class LocationsInline(AbstractLocationsInline):
    """Inline admin for locations."""

    model = models.Proposition.locations.through


class PremisesInline(TabularInline):
    """Inline admin for a proposition's premises."""

    model = models.ArgumentSupport

    autocomplete_fields = ['premise']
    exclude = ['conclusion']
    extra = 0
    sortable_field_name = 'position'
    verbose_name = 'premise'
    verbose_name_plural = 'premises'

    def get_queryset(self, request: 'HttpRequest') -> 'QuerySet':
        """Return the queryset of model instances to be included."""
        return super().get_queryset(request).select_related('premise')


class ArgumentsInline(TabularInline):
    """Inline admin for a proposition's supported propositions."""

    model = models.Argument

    extra = 0
    fields = ('position', 'type', '__html__', 'explanation')
    fk_name = 'conclusion'
    readonly_fields = ('__html__',)
    show_change_link = True
    verbose_name = 'argument'
    verbose_name_plural = 'arguments'

    def get_queryset(self, request: 'HttpRequest') -> 'QuerySet':
        """Return the queryset of model instances to be included."""
        return super().get_queryset(request).order_by('position')
