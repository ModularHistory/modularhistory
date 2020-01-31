from django.contrib.admin import SimpleListFilter
from polymorphic.admin import (PolymorphicParentModelAdmin, PolymorphicChildModelAdmin,
                               PolymorphicInlineSupportMixin)

from admin import admin_site, Admin, TabularInline, StackedInline
from quotes.models import QuoteSourceReference
from occurrences.models import Occurrence
from . import models
from django.db.models import Q


class HasFileFilter(SimpleListFilter):
    title = 'has file'
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


class HasPageNumber(SimpleListFilter):
    title = 'has page number'
    parameter_name = 'has_page_number'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.filter(file__isnull=False).exclude(file='')
        ids = []
        if self.value() == 'Yes':
            for source in queryset:
                obj = source.object if hasattr(source, 'object') else source
                if hasattr(obj, 'page_number'):
                    if obj.page_number:
                        ids.append(source.id)
            return queryset.filter(id__in=ids)
        if self.value() == 'No':
            for source in queryset:
                obj = source.object if hasattr(source, 'object') else source
                if hasattr(obj, 'page_number'):
                    if not obj.page_number:
                        ids.append(source.id)
            return queryset.filter(id__in=ids)


class HasFilePageOffsetFilter(SimpleListFilter):
    title = 'has file page offset'
    parameter_name = 'has_file_page_offset'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        sources_with_files = queryset.filter(file__isnull=False).exclude(file='')
        ids = []
        if self.value() == 'Yes':
            for source in sources_with_files:
                file = source.file
                if file.page_offset:
                    ids.append(source.id)
            return sources_with_files.filter(id__in=ids)
        elif self.value() == 'No':
            for source in sources_with_files:
                file = source.file
                if not file.page_offset:
                    ids.append(source.id)
            return sources_with_files.filter(id__in=ids)


class ImpreciseDateFilter(SimpleListFilter):
    title = 'date is imprecise'
    parameter_name = 'date_is_imprecise'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            # ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(date__second='01', date__minute='01', date__hour='01')
        # if self.value() == 'No':
        #     return queryset


class AttributeesInline(TabularInline):
    model = models.Source.attributees.through
    extra = 1
    autocomplete_fields = ['attributee']


class ContainersInline(StackedInline):
    model = models.Source.containers.through
    fk_name = 'source'
    extra = 1
    autocomplete_fields = ['container']


class QuotesInline(StackedInline):
    model = QuoteSourceReference
    extra = 1
    autocomplete_fields = ['quote']


class OccurrencesInline(StackedInline):
    model = Occurrence.sources.through
    extra = 1
    autocomplete_fields = ['occurrence']


class SourceAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, Admin):
    base_model = models.Source
    child_models = [
        models.Book,
        models.Article,
        models.Lecture,
        models.Speech,
        models.Interview,
        models.Essay,
        models.Document,
        models.Letter,
        models.Documentary
    ]
    list_display = ('string', 'creators', 'title', 'date_string', 'location', 'admin_file_link')
    list_filter = (HasFileFilter, HasFilePageOffsetFilter, HasPageNumber,
                   ImpreciseDateFilter, 'attributees', 'polymorphic_ctype')
    exclude = ['db_string']
    search_fields = models.Source.searchable_fields
    ordering = ('date', 'title', 'creators', 'polymorphic_ctype')
    inlines = [AttributeesInline, ContainersInline, QuotesInline, OccurrencesInline]


class ChildModelAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, Admin):
    base_model = models.Source
    list_display = ('string', 'description', 'date_string')
    list_filter = ('year', 'attributees')
    exclude = ['db_string']
    search_fields = ('db_string',)
    ordering = ('date', 'creators', 'title')
    inlines = SourceAdmin.inlines

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('number', 'page_number', 'end_page_number', 'container', 'description', 'citations'):
            if field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields


class NumbersInline(TabularInline):
    model = models.PublicationNumber
    extra = 1
    autocomplete_fields = ['volume', 'publication']
    show_change_link = True


class VolumesInline(TabularInline):
    model = models.PublicationVolume
    extra = 1
    autocomplete_fields = ['publication']
    show_change_link = True


class PublicationAdmin(Admin):
    list_display = ('__str__', 'description', 'type')
    search_fields = ('name',)
    list_filter = ('type',)
    inlines = [VolumesInline, NumbersInline]


class ArticleAdmin(ChildModelAdmin):
    list_display = ('string', 'publication', 'description', 'date_string')
    autocomplete_fields = ['publication', 'volume', 'number']


class ArticlesInline(StackedInline):
    model = models.Article
    extra = 1


class SpeechAdmin(ChildModelAdmin):
    list_display = ('string', 'type', 'venue', 'date_string')
    search_fields = ('db_string', 'location__name')


class PublicationVolumeAdmin(Admin):
    search_fields = ('number', 'publication__name')
    inlines = [NumbersInline, ArticlesInline]
    autocomplete_fields = ('publication',)


class PublicationNumberAdmin(Admin):
    search_fields = ('number', 'publication__name')
    inlines = [ArticlesInline]
    autocomplete_fields = ('publication', 'volume')


admin_site.register(models.Book, ChildModelAdmin)
admin_site.register(models.Lecture, ChildModelAdmin)
admin_site.register(models.Interview, ChildModelAdmin)
admin_site.register(models.Speech, SpeechAdmin)
admin_site.register(models.Essay, ChildModelAdmin)
admin_site.register(models.Document, ChildModelAdmin)
admin_site.register(models.Letter, ChildModelAdmin)
admin_site.register(models.Article, ArticleAdmin)
admin_site.register(models.Documentary, ChildModelAdmin)
admin_site.register(models.Source, SourceAdmin)
admin_site.register(models.Publication, PublicationAdmin)
admin_site.register(models.Collection, Admin)
admin_site.register(models.PublicationVolume, PublicationVolumeAdmin)
admin_site.register(models.PublicationNumber, PublicationNumberAdmin)
admin_site.register(models.Repository, Admin)
# admin_site.register(SourceAttribution)
