from django.db.models.query import QuerySet

from apps.admin.admin_site import admin_site
from apps.admin.inlines import TabularInline
from apps.entities.admin.filters import RelatedEntityFilter
from apps.entities.admin.inlines import AbstractRelatedEntitiesInline
from apps.images.admin import AbstractImagesInline
from apps.places.admin import AbstractLocationsInline
from apps.propositions import models
from apps.propositions.admin.filters import (
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.citations import AbstractSourcesInline
from apps.sources.admin.filters import HasMultipleSourcesFilter, HasSourceFilter
from apps.topics.admin.tags import AbstractTagsInline
from apps.topics.models.taggable_model import TopicFilter


class TagsInline(AbstractTagsInline):
    """Inline admin for topic tags."""

    model = models.TypedProposition.tags.through


class SourcesInline(AbstractSourcesInline):
    """Inline admin for sources."""

    model = models.TypedProposition.sources.through


class RelatedEntitiesInline(AbstractRelatedEntitiesInline):
    """Inline admin for related entities."""

    model = models.TypedProposition.related_entities.through


class ImagesInline(AbstractImagesInline):
    """Inline admin for images."""

    model = models.TypedProposition.images.through


class LocationsInline(AbstractLocationsInline):
    """Inline admin for locations."""

    model = models.TypedProposition.locations.through


class ConclusionsInline(TabularInline):
    """Inline admin for a proposition's supported propositions."""

    verbose_name = 'supported proposition'
    verbose_name_plural = 'supported propositions'
    model = models.Support
    exclude = ['position']
    fk_name = 'premise'
    autocomplete_fields = ['conclusion']
    extra = 0

    def get_queryset(self, request):
        """Return the queryset of model instances to be included."""
        return super().get_queryset(request).select_related('premise', 'conclusion')


class PremisesInline(TabularInline):
    """Inline admin for a proposition's premises."""

    verbose_name = 'premise'
    verbose_name_plural = 'premises'
    model = models.Support
    fk_name = 'conclusion'
    autocomplete_fields = ['premise']
    extra = 0

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_queryset(self, request) -> QuerySet:
        """Return the queryset of model instances to be included."""
        return super().get_queryset(request).select_related('premise', 'conclusion')


class AbstractPropositionAdmin(SearchableModelAdmin):
    """Abstract base admin for propositions."""

    exclude = SearchableModelAdmin.exclude + [
        'related_entities',
        'sources',
        'images',
        'locations',
    ]
    inlines = [
        PremisesInline,
        ConclusionsInline,
        SourcesInline,
        ImagesInline,
        RelatedEntitiesInline,
        TagsInline,
        LocationsInline,
    ]
    list_display = [
        'slug',
        'escaped_summary',
        'tags_string',
    ]
    list_filter = [
        'verified',
        TopicFilter,
        RelatedEntityFilter,
        HasDateFilter,
        HasQuotesFilter,
        LocationFilter,
        HasSourceFilter,
        HasMultipleSourcesFilter,
        # HasMultipleImagesFilter,
    ]
    list_per_page = 20


class PolymorphicPropositionAdmin(AbstractPropositionAdmin):
    """Admin for all propositions."""

    model = models.TypedProposition

    list_display = AbstractPropositionAdmin.list_display + ['date_string', 'type']
    list_filter = AbstractPropositionAdmin.list_filter + ['type']
    ordering = ['date', 'type']
    search_fields = model.searchable_fields


class PropositionAdmin(AbstractPropositionAdmin):
    """Admin for propositions."""


admin_site.register(models.TypedProposition, PolymorphicPropositionAdmin)
admin_site.register(models.Proposition, PropositionAdmin)
