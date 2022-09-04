from rangefilter.filters import DateRangeFilter

from apps.admin.admin_site import admin_site
from apps.admin.model_admin import ExtendedModelAdmin
from apps.collections.admin import AbstractCollectionsInline, CollectionFilter
from apps.entities.admin.filters import RelatedEntityFilter
from apps.propositions import models
from apps.propositions.admin.filters import HasDateFilter, HasQuotesFilter, LocationFilter
from apps.propositions.admin.inlines import (
    ArgumentsInline,
    ConflictsInline,
    ImagesInline,
    LocationsInline,
    PremiseGroupsInline,
    PremisesInline,
    RelatedEntitiesInline,
    SourcesInline,
    TagsInline,
)
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.filters import HasMultipleSourcesFilter, HasSourceFilter
from apps.topics.admin.filter import TopicFilter


class CollectionsInline(AbstractCollectionsInline):
    """Inline admin for collections."""

    model = models.CollectionInclusion


class AbstractPropositionAdmin(SearchableModelAdmin):
    """Abstract base admin for propositions."""

    exclude = [
        *SearchableModelAdmin.exclude,
        'conflicting_propositions',
        'related_entities',
        'sources',
        'images',
        'locations',
        'related_quotes',
    ]
    inlines = [
        ArgumentsInline,
        SourcesInline,
        ConflictsInline,
        ImagesInline,
        RelatedEntitiesInline,
        LocationsInline,
        CollectionsInline,
        TagsInline,
    ]
    list_display = [
        'slug',
        'escaped_summary',
        'tags_string',
    ]
    list_filter = [
        'verified',
        TopicFilter,
        CollectionFilter,
        RelatedEntityFilter,
        HasDateFilter,
        HasQuotesFilter,
        LocationFilter,
        HasSourceFilter,
        HasMultipleSourcesFilter,
        # HasMultipleImagesFilter,
        ('date', DateRangeFilter),
    ]
    list_per_page = 20


class PropositionAdmin(AbstractPropositionAdmin):
    """Admin for all propositions."""

    model = models.Proposition

    list_display = [*AbstractPropositionAdmin.list_display, 'date_string', 'type']
    list_filter = ['type', *AbstractPropositionAdmin.list_filter]
    ordering = ['date', 'type']
    search_fields = model.searchable_fields


class PublicationAdmin(AbstractPropositionAdmin):
    """Admin for publications (as occurrences)."""

    model = models.Publication
    search_fields = model.searchable_fields


class ArgumentAdmin(ExtendedModelAdmin):
    """Admin for arguments."""

    model = models.Argument
    inlines = [PremisesInline, PremiseGroupsInline]


admin_site.register(models.Proposition, PropositionAdmin)
admin_site.register(models.Publication, PublicationAdmin)
admin_site.register(models.Argument, ArgumentAdmin)
