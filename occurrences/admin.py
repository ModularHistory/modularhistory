from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q
from django.urls import path

from history.admin import admin_site, Admin, TabularInline
from history.models.taggable_model import TopicFilter
from occurrences import models
from quotes.admin import RelatedQuotesInline
from sources.admin import CitationsInline
from topics.admin import RelatedTopicsInline
from topics.views import TagSearchView


class EntityFilter(AutocompleteFilter):
    """TODO: add docstring."""

    title = 'entity'
    field_name = 'involved_entities'


# class TopicFilter(AutocompleteFilter):
#     title = 'topic'
#     field_name = 'related_topics'


class LocationFilter(AutocompleteFilter):
    """TODO: add docstring."""

    title = 'location'
    field_name = 'locations'


class HasQuotesFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has quotes'
    parameter_name = 'has_quotes'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        queryset = queryset.annotate(quote_count=Count('quote_relations'))
        if self.value() == 'Yes':
            return queryset.exclude(quote_count__lt=1)
        if self.value() == 'No':
            return queryset.filter(quote_count__gt=1)
        return queryset


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


class HasDateFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has date'
    parameter_name = 'has_date'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.filter(date__isnull=False).exclude(date='')
        if self.value() == 'No':
            return queryset.filter(Q(date__isnull=True) | Q(date=''))


class OccurrenceAdmin(Admin):
    """TODO: add docstring."""

    base_model = models.Occurrence
    list_display = (
        'pk',
        'summary',
        'detail_link',
        'description__truncated',
        'date_string',
        # 'tags_string'
    )
    list_filter = [
        'verified', HasDateFilter, HasQuotesFilter,
        EntityFilter,
        TopicFilter,
        LocationFilter
    ]
    search_fields = models.Occurrence.searchable_fields
    ordering = ('date',)
    inlines = [
        RelatedQuotesInline, InvolvedEntitiesInline,
        LocationsInline, ImagesInline,
        CitationsInline,
        RelatedTopicsInline
    ]

    def get_urls(self):
        """TODO: add docstring."""
        urls = super().get_urls()
        custom_urls = [
            path('tag_search/',
                 self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                 name='tag_search'),
        ]
        return custom_urls + urls


class OccurrenceChainAdmin(Admin):
    """TODO: add docstring."""

    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
