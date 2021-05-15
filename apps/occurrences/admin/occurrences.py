"""Admin classes for occurrences."""

from apps.admin import ModelAdmin, admin_site
from apps.occurrences import models
from apps.occurrences.admin.occurrence_filters import (
    EntityFilter,
    HasDateFilter,
    HasQuotesFilter,
    LocationFilter,
)
from apps.occurrences.admin.occurrence_inlines import (  # PostulationsInline,
    ImagesInline,
    InvolvedEntitiesInline,
    LocationsInline,
    OccurrencesInline,
)
from apps.quotes.admin.related_quotes_inline import RelatedQuotesInline
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin import CitationsInline
from apps.sources.admin.filters import HasMultipleCitationsFilter, HasSourceFilter
from apps.topics.admin import RelatedTopicsInline
from apps.topics.models.taggable_model import TopicFilter

# class _ImagesInline(AbstractImagesInline):
#     """Inline admin for an occurrence's images."""

#     model = models.NewOccurrence.images.through
#     readonly_fields = []


# class _InvolvedEntitiesInline(InvolvedEntitiesInline):
#     """Inline admin for an occurrence's images."""

#     model = models.NewOccurrence.involved_entities.through


# class _RelatedEntitiesInline(InvolvedEntitiesInline):
#     """Inline admin for an occurrence's images."""

#     model = models.NewOccurrence.related_entities.through


# class _LocationsInline(LocationsInline):
#     """Inline admin for an occurrence's locations."""

#     model = models.NewOccurrence.related_entities.through


# class NewOccurrenceAdmin(PropositionChildAdmin):
#     """Model admin for occurrences."""

#     model = models.Occurrence

#     exclude = SearchableModelAdmin.exclude + [
#         'postulations',
#         # Use inlines for m2m relations.
#         'images',
#         'related_entities',
#         'locations',
#     ]
#     inlines = [
#         RelatedQuotesInline,
#         # InvolvedEntitiesInline,
#         # LocationsInline,
#         _ImagesInline,
#         CitationsInline,
#         RelatedTopicsInline,
#     ]
#     list_display = [
#         'slug',
#         'title',
#         'summary',
#         'date_string',
#     ]
#     list_editable = ['title']
#     list_filter = [
#         'verified',
#         HasDateFilter,
#         HasQuotesFilter,
#         TopicFilter,
#         LocationFilter,
#         HasSourceFilter,
#         HasMultipleCitationsFilter,
#         HasMultipleImagesFilter,
#     ]
#     list_per_page = 10
#     ordering = ['date']
#     readonly_fields = SearchableModelAdmin.readonly_fields
#     search_fields = model.searchable_fields

#     # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
#     date_hierarchy = 'date'


class OccurrenceAdmin(SearchableModelAdmin):
    """Model admin for occurrences."""

    model = models.Occurrence

    exclude = SearchableModelAdmin.exclude + ['postulations']
    inlines = [
        RelatedQuotesInline,
        InvolvedEntitiesInline,
        LocationsInline,
        ImagesInline,
        CitationsInline,
        RelatedTopicsInline,
    ]
    list_display = [
        'slug',
        'title',
        'summary',
        # 'detail_link',
        'date_string',
    ]
    list_editable = ['title']
    list_filter = [
        'verified',
        HasDateFilter,
        HasQuotesFilter,
        EntityFilter,
        TopicFilter,
        LocationFilter,
        HasSourceFilter,
        HasMultipleCitationsFilter,
    ]
    list_per_page = 10
    ordering = ['date']
    readonly_fields = SearchableModelAdmin.readonly_fields
    search_fields = model.searchable_fields

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'


class OccurrenceChainAdmin(ModelAdmin):
    """Admin for occurrence chains."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
# admin_site.register(models.NewOccurrence, NewOccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
