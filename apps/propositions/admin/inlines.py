from typing import TYPE_CHECKING

from nested_admin import NestedStackedInline, NestedTabularInline

from apps.entities.admin.inlines import AbstractRelatedEntitiesInline
from apps.images.admin import AbstractImagesInline
from apps.places.admin import AbstractLocationsInline
from apps.propositions import models
from apps.sources.admin.citations import AbstractSourcesInline
from apps.topics.admin.tags import AbstractTagsInline

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest


class TagsInline(AbstractTagsInline, NestedTabularInline):
    """Inline admin for topic tags."""

    model = models.PolymorphicProposition.tags.through


class SourcesInline(AbstractSourcesInline, NestedTabularInline):
    """Inline admin for sources."""

    model = models.PolymorphicProposition.sources.through


class RelatedEntitiesInline(AbstractRelatedEntitiesInline, NestedTabularInline):
    """Inline admin for related entities."""

    model = models.PolymorphicProposition.related_entities.through


class ImagesInline(AbstractImagesInline, NestedTabularInline):
    """Inline admin for images."""

    model = models.PolymorphicProposition.images.through


class LocationsInline(AbstractLocationsInline, NestedTabularInline):
    """Inline admin for locations."""

    model = models.PolymorphicProposition.locations.through


class PremisesInline(NestedTabularInline):
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


class ArgumentsInline(NestedStackedInline):
    """Inline admin for a proposition's supported propositions."""

    model = models.Argument

    extra = 0
    inlines = [PremisesInline]
    verbose_name = 'argument'
    verbose_name_plural = 'arguments'

    def get_queryset(self, request: 'HttpRequest') -> 'QuerySet':
        """Return the queryset of model instances to be included."""
        return super().get_queryset(request).order_by('type')
