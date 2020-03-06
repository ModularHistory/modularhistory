from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicInlineSupportMixin
)

from admin import admin_site, Admin, TabularInline, StackedInline
from occurrences.models import Occurrence
from quotes.models import QuoteSourceReference
from . import models
from .list_filters import HasFileFilter, HasFilePageOffsetFilter, HasPageNumber, ImpreciseDateFilter


class AttributeesInline(TabularInline):
    model = models.Source.attributees.through
    extra = 1
    autocomplete_fields = ['attributee']


class ContainersInline(TabularInline):
    verbose_name = 'container'
    verbose_name_plural = 'containers'
    model = models.Source.containers.through
    fk_name = 'source'
    extra = 0
    autocomplete_fields = ['container']


class ContainedSourcesInline(TabularInline):
    verbose_name = 'contained source'
    verbose_name_plural = 'contained sources'
    model = models.Source.containers.through
    fk_name = 'container'
    extra = 0
    autocomplete_fields = ['container']


class QuotesInline(TabularInline):
    model = QuoteSourceReference
    extra = 1
    autocomplete_fields = ['quote']


class OccurrencesInline(TabularInline):
    model = Occurrence.sources.through
    extra = 1
    autocomplete_fields = ['occurrence']


class SourceAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, Admin):
    base_model = models.Source
    child_models = [
        models.Book,
        models.Chapter,
        models.Article,
        models.Speech,
        models.Interview,
        models.Piece,
        models.Document,
        models.JournalEntry,
        models.Letter,
        models.Documentary,
        models.WebPage,
        models.Affidavit
    ]
    list_display = (
        'string',
        'creators',
        'date_string',
        'location',
        'admin_file_link'
    )
    list_filter = (
        HasFileFilter,
        HasFilePageOffsetFilter,
        HasPageNumber,
        ImpreciseDateFilter,
        'hidden',
        'attributees',
        'polymorphic_ctype'
    )
    readonly_fields = ['db_string']
    search_fields = models.Source.searchable_fields
    ordering = (
        'date',
        'creators',
        'polymorphic_ctype'
    )
    inlines = [AttributeesInline, ContainersInline, ContainedSourcesInline, QuotesInline, OccurrencesInline]
    autocomplete_fields = ['file', 'location']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'database_string' in fields:
            fields.remove('database_string')
            fields.insert(0, 'database_string')


class ChildModelAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, Admin):
    base_model = models.Source
    list_display = ['string', 'description', 'date_string']
    list_filter = ['attributees']
    readonly_fields = ['db_string']
    search_fields = ['db_string']
    ordering = ['date', 'creators']
    inlines = SourceAdmin.inlines
    autocomplete_fields = SourceAdmin.autocomplete_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        for field_name in ('title',):
            if field_name in fields:
                fields.remove(field_name)
                fields.insert(0, field_name)

        for field_name in (
                'volume', 'number', 'page_number', 'end_page_number',
                'container', 'description', 'citations'
        ):
            if field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields


class PublicationAdmin(Admin):
    list_display = ('__str__', 'description', 'type2')
    search_fields = ('name',)
    list_filter = ('type2',)


class ArticleAdmin(ChildModelAdmin):
    list_display = ('string', 'publication', 'description', 'date_string')
    autocomplete_fields = ChildModelAdmin.autocomplete_fields + ['publication']


class ArticlesInline(StackedInline):
    model = models.Article
    extra = 1


class SpeechAdmin(ChildModelAdmin):
    list_display = ('string', 'type2', 'location', 'date_string')
    search_fields = ('db_string', 'location__name')


class CollectionAdmin(Admin):
    search_fields = ('name', 'repository__name', 'repository__location')
    autocomplete_fields = ('repository',)


class DocumentAdmin(ChildModelAdmin):
    search_fields = ChildModelAdmin.search_fields
    autocomplete_fields = ('collection', 'file')


class RepositoryAdmin(Admin):
    search_fields = ('name', 'location')


class SourcesInline(TabularInline):
    model = models.Source
    extra = 0
    fields = ['verified', 'hidden', 'date_is_circa', 'creators', 'link', 'date', 'publication_date']


class SourceFileAdmin(Admin):
    list_display = ('__str__', 'name', 'page_offset')
    search_fields = ('file',)
    inlines = [SourcesInline]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if fields and 'page_offset' in fields:
            fields.remove('page_offset')
            fields.append('page_offset')
        return fields


admin_site.register(models.Source, SourceAdmin)

admin_site.register(models.Article, ArticleAdmin)

admin_site.register(models.Speech, SpeechAdmin)

admin_site.register(models.SourceFile, SourceFileAdmin)
admin_site.register(models.Collection, CollectionAdmin)
admin_site.register(models.Repository, RepositoryAdmin)
admin_site.register(models.Document, DocumentAdmin)
admin_site.register(models.Letter, DocumentAdmin)

admin_site.register(models.JournalEntry, ChildModelAdmin)

admin_site.register(models.Publication, PublicationAdmin)

child_models = (
    models.Book,
    models.Chapter,
    models.Interview,
    models.Piece,
    models.Documentary,
    models.WebPage,
    models.Affidavit
)

for child in child_models:
    admin_site.register(child, ChildModelAdmin)
