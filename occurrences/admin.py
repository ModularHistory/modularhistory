from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from admin import admin_site, Admin, TabularInline  # , StackedInline
from sources.admin import CitationsInline
from topics.models import OccurrenceTopicRelation
from . import models


class EntityFilter(AutocompleteFilter):
    title = 'entity'
    field_name = 'involved_entities'


class TopicFilter(AutocompleteFilter):
    title = 'topic'
    field_name = 'related_topics'


class LocationFilter(AutocompleteFilter):
    title = 'location'
    field_name = 'locations'


class LocationsInline(TabularInline):
    model = models.Occurrence.locations.through
    extra = 1
    autocomplete_fields = ['location']


class ImagesInline(TabularInline):
    model = models.Occurrence.images.through
    extra = 0
    autocomplete_fields = ['image']
    readonly_fields = ['key', 'image_pk']


class RelatedQuotesInline(TabularInline):
    model = models.Occurrence.related_quotes.through
    autocomplete_fields = ['quote']
    readonly_fields = ['pk', 'quote_pk']

    sortable_field_name = 'position'

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.related_quotes.count():
            return 0
        return 1


class RelatedTopicsInline(TabularInline):
    model = OccurrenceTopicRelation
    extra = 1
    autocomplete_fields = ['topic']


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
        # 'date',
        'related_topics_string'
    )
    list_filter = ['verified', HasDateFilter, EntityFilter, TopicFilter, LocationFilter]
    search_fields = models.Occurrence.searchable_fields
    ordering = ('date',)
    inlines = [
        RelatedQuotesInline, InvolvedEntitiesInline,
        LocationsInline, ImagesInline,
        CitationsInline,
        RelatedTopicsInline
    ]


class OccurrenceChainAdmin(Admin):
    base_model = models.OccurrenceChain
    inlines = [OccurrencesInline]


admin_site.register(models.Occurrence, OccurrenceAdmin)
admin_site.register(models.OccurrenceChain, OccurrenceChainAdmin)
