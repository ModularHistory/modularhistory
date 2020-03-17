from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter
from django.contrib.admin import TabularInline

from admin import admin_site, Admin
from occurrences.models import Occurrence
from topics.models import TopicQuoteRelation
from . import models


class TopicFilter(AutocompleteFilter):
    title = 'topic'
    field_name = 'related_topics'


class AttributeeFilter(AutocompleteFilter):
    title = 'attributee'
    field_name = 'attributee'


class AttributeeClassificationFilter(AutocompleteFilter):
    title = 'attributee classification'
    field_name = 'attributee__classifications'


class HasSourceFilter(SimpleListFilter):
    title = 'has source'
    parameter_name = 'has_source'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.exclude(sources=None)
        if self.value() == 'No':
            return queryset.filter(sources=None)


class SourceReferencesInline(TabularInline):
    model = models.Quote.sources.through
    autocomplete_fields = ['source']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.citations.count():
            return 0
        return 1


class OccurrencesInline(TabularInline):
    model = Occurrence.related_quotes.through
    autocomplete_fields = ['occurrence']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.related_occurrences.count():
            return 0
        return 1


class TopicsInline(TabularInline):
    model = TopicQuoteRelation
    extra = 1
    autocomplete_fields = ['topic']


class BitesInline(TabularInline):
    model = models.QuoteBite
    extra = 0


# class QuoteForm(ModelForm):
#     fields = []
#
#     class Meta:
#         model = models.Quote


class QuoteAdmin(Admin):
    # form = QuoteForm
    list_display = [
        'bite',
        'detail_link',
        'attributee',
        'date_string',
        'citation_html',
        'topic_tags'
    ]
    list_filter = [
        'verified',
        HasSourceFilter,
        TopicFilter,
        AttributeeFilter,
        # AttributeeClassificationFilter  # broken
        'attributee__classifications'
    ]
    search_fields = models.Quote.searchable_fields
    ordering = ('date', 'attributee')
    autocomplete_fields = ['attributee']
    readonly_fields = ['citation_html']
    inlines = [
        SourceReferencesInline,
        OccurrencesInline,
        TopicsInline,
        BitesInline
    ]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('date', 'date_is_circa'):
            if fields and field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields


admin_site.register(models.Quote, QuoteAdmin)
# admin_site.register(SourceReference)
