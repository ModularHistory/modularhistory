"""Admin classes for occurrences."""

from apps.admin.admin_site import admin_site
from apps.propositions import models
from apps.propositions.admin.filters import (
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from apps.propositions.admin.propositions import TypedPropositionAdmin
from apps.sources.admin.filters import HasMultipleSourcesFilter, HasSourceFilter
from apps.topics.models.taggable_model import TopicFilter


class OccurrenceAdmin(TypedPropositionAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence

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
