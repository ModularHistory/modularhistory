from django.contrib.admin import TabularInline

from admin import admin_site, Admin
from occurrences.models import Occurrence
from topics.models import TopicQuoteRelation
from . import models


# from django.forms import ModelForm


class SourceReferencesInline(TabularInline):
    model = models.Quote.sources.through
    autocomplete_fields = ['source']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.source_references.count():
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
    list_display = ('bite', 'attributee', 'date_string', 'source_reference', 'topic_tags', 'id')
    list_filter = ['attributee']
    search_fields = models.Quote.searchable_fields
    ordering = ('date', 'attributee')
    autocomplete_fields = ['attributee']
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
