from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q
from admin import admin_site, Admin, TabularInline, GenericTabularInline
from quotes.admin import RelatedQuotesInline
from sources.admin import CitationsInline
from topics.admin import RelatedTopicsInline
from . import models


class EntityFilter(AutocompleteFilter):
    title = 'entity'
    field_name = 'involved_entities'


# class TopicFilter(AutocompleteFilter):
#     title = 'topic'
#     field_name = 'related_topics'


class LocationFilter(AutocompleteFilter):
    title = 'location'
    field_name = 'locations'


class HasQuotesFilter(SimpleListFilter):
    title = 'has quotes'
    parameter_name = 'has_quotes'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(quote_count=Count('quote_relations'))
        if self.value() == 'Yes':
            return queryset.exclude(quote_count__lt=1)
        if self.value() == 'No':
            return queryset.filter(quote_count__gt=1)
        return queryset


class LocationsInline(TabularInline):
    model = models.Occurrence.locations.through
    extra = 1
    autocomplete_fields = ['location']


class ImagesInline(TabularInline):
    model = models.Occurrence.images.through
    extra = 0
    autocomplete_fields = ['image']
    readonly_fields = ['key', 'image_pk']


class InvolvedEntitiesInline(TabularInline):
    model = models.Occurrence.involved_entities.through
    extra = 1
    autocomplete_fields = ['entity']


class OccurrencesInline(TabularInline):
    model = models.Occurrence.chains.through
    autocomplete_fields = ['occurrence']
    extra = 1


class HasDateFilter(SimpleListFilter):
    title = 'has date'
    parameter_name = 'has_date'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(date__isnull=False).exclude(date='')
        if self.value() == 'No':
            return queryset.filter(Q(date__isnull=True) | Q(date=''))


class OccurrenceAdmin(Admin):
    base_model = models.Occurrence
    list_display = (
        'pk',
        'summary',
        'detail_link',
        'description__truncated',
        'date_string',
        # 'related_topics_string'
    )
    list_filter = [
        'verified', HasDateFilter, HasQuotesFilter,
        EntityFilter,
        # TopicFilter,
        LocationFilter
    ]
    search_fields = models.Occurrence.searchable_fields
    ordering = ('date',)
    inlines = [
        RelatedQuotesInline, InvolvedEntitiesInline,
        LocationsInline, ImagesInline,
        CitationsInline,
        # RelatedTopicsInline
    ]


class OccurrenceChainAdmin(Admin):
    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
