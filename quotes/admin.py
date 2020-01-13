from django.contrib.admin import TabularInline, StackedInline
from django.forms import ModelForm

from admin import admin_site, Admin
from entities.models import Entity
from occurrences.models import Occurrence
from topics.models import TopicQuoteRelation
from . import models


class SourceReferencesInline(StackedInline):
    model = models.Quote.sources.through
    extra = 1


class AttributeeInline(TabularInline):
    model = Entity
    extra = 1


class OccurrencesInline(TabularInline):
    model = Occurrence.related_quotes.through
    extra = 1


class TopicsInline(TabularInline):
    model = TopicQuoteRelation
    extra = 1


class QuoteForm(ModelForm):
    class Meta:
        model = models.Quote
        exclude = ['year']


class QuoteAdmin(Admin):
    form = QuoteForm
    list_display = ('bite', 'attributee', 'date', 'source_reference', 'topic_tags')
    list_filter = ('attributee', 'year')
    search_fields = models.Quote.searchable_fields
    ordering = ('date', 'attributee')
    inlines = [
        # AttributeeInline,
        SourceReferencesInline,
        OccurrencesInline,
        TopicsInline
    ]


admin_site.register(models.Quote, QuoteAdmin)
# admin_site.register(SourceReference)
