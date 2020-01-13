from django.contrib.admin import TabularInline, StackedInline, SimpleListFilter
from polymorphic.admin import (PolymorphicParentModelAdmin, PolymorphicChildModelAdmin,
                               PolymorphicInlineSupportMixin)

from admin import admin_site, Admin
from quotes.models import QuoteSourceReference
from occurrences.models import Occurrence
from . import models
from django.db.models import Q


class HasFileFilter(SimpleListFilter):
    title = 'Has file'
    parameter_name = 'has_file'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(file__isnull=False).exclude(file='')
        if self.value() == 'No':
            return queryset.filter(Q(file__isnull=True) | Q(file=''))


class ImpreciseDateFilter(SimpleListFilter):
    title = 'Date is imprecise'
    parameter_name = 'date_is_imprecise'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            # ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(date__month='01', date__day='01')
        # if self.value() == 'No':
        #     return queryset


class AttributeesInline(TabularInline):
    model = models.Source.attributees.through
    extra = 1


class QuotesInline(StackedInline):
    model = QuoteSourceReference
    extra = 1
    fields = ('quote', 'page_number', 'end_page_number', 'position', 'notes')


class OccurrencesInline(StackedInline):
    model = Occurrence.sources.through
    extra = 1
    fields = ('occurrence', 'page_number', 'end_page_number', 'source_type', 'position', 'notes')


class SourceAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, Admin):
    base_model = models.Source
    child_models = [
        models.Book,
        models.JournalArticle,
        models.NewspaperArticle,
        models.MagazineArticle,
        models.Lecture,
        models.Speech,
        models.Interview,
        models.Essay,
        models.Document,
        models.Letter,
        models.Documentary
    ]
    list_display = ('creators', 'title', 'description', 'date', 'polymorphic_ctype')
    list_filter = (HasFileFilter, ImpreciseDateFilter, 'year', 'attributees')
    search_fields = ('creators', 'title', 'description')
    ordering = ('date', 'title', 'creators', 'polymorphic_ctype')
    inlines = [AttributeesInline, QuotesInline, OccurrencesInline]


class ChildModelAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, Admin):
    base_model = models.Source
    list_display = ('__str__', 'description', 'date')
    list_filter = ('year', 'attributees')
    search_fields = ('__str__',)
    ordering = ('date', 'creators', 'title')
    inlines = SourceAdmin.inlines

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('number', 'page_number', 'end_page_number', 'container', 'description', 'citations'):
            if field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields


admin_site.register(models.Book, ChildModelAdmin)
admin_site.register(models.JournalArticle, ChildModelAdmin)
admin_site.register(models.NewspaperArticle, ChildModelAdmin)
admin_site.register(models.MagazineArticle, ChildModelAdmin)
admin_site.register(models.Lecture, ChildModelAdmin)
admin_site.register(models.Interview, ChildModelAdmin)
admin_site.register(models.Speech, ChildModelAdmin)
admin_site.register(models.Essay, ChildModelAdmin)
admin_site.register(models.Document, ChildModelAdmin)
admin_site.register(models.Letter, ChildModelAdmin)
admin_site.register(models.Documentary, ChildModelAdmin)
admin_site.register(models.Source, SourceAdmin)
admin_site.register(models.Newspaper, Admin)
admin_site.register(models.Journal, Admin)
admin_site.register(models.Magazine, Admin)
# admin_site.register(SourceAttribution)
