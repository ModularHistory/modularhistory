from apps.admin.admin_site import admin_site
from apps.admin.model_admin import NestedModelAdmin
from apps.entities.admin.filters import RelatedEntityFilter
from apps.propositions import models
from apps.propositions.admin.filters import HasDateFilter, HasQuotesFilter, LocationFilter
from apps.propositions.admin.inlines import (
    ArgumentsInline,
    ImagesInline,
    LocationsInline,
    RelatedEntitiesInline,
    SourcesInline,
    TagsInline,
)
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.filters import HasMultipleSourcesFilter, HasSourceFilter
from apps.topics.models.taggable_model import TopicFilter


class AbstractPropositionAdmin(NestedModelAdmin, SearchableModelAdmin):
    """Abstract base admin for propositions."""

    exclude = SearchableModelAdmin.exclude + [
        'related_entities',
        'sources',
        'images',
        'locations',
    ]
    inlines = [
        ArgumentsInline,
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


class PropositionAdmin(AbstractPropositionAdmin):
    """Admin for all propositions."""

    model = models.Proposition

    list_display = AbstractPropositionAdmin.list_display + ['date_string', 'type']
    list_filter = AbstractPropositionAdmin.list_filter + ['type']
    ordering = ['date', 'type']
    search_fields = model.searchable_fields


admin_site.register(models.Proposition, PropositionAdmin)
admin_site.register(models.Conclusion, PropositionAdmin)
admin_site.register(models.Occurrence, PropositionAdmin)
