from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin
)

from admin import GenericTabularInline
from admin import admin_site, Admin, TabularInline, StackedInline, PolymorphicInlineSupportMixin
from .filters import HasFileFilter, HasFilePageOffsetFilter, HasPageNumber, ImpreciseDateFilter
from .. import models


class AttributeesInline(TabularInline):
    model = models.Source.attributees.through
    autocomplete_fields = ['attributee']

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.attributees.count():
            return 0
        return 1


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
    autocomplete_fields = ['source']


class RelatedInline(GenericTabularInline):
    model = models.Citation
    extra = 0
    verbose_name = 'related object'
    verbose_name_plural = 'related objects (not yet implemented)'

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'


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
    list_display = [
        'string',
        'creators',
        'date_string',
        'location',
        'admin_file_link'
    ]
    list_filter = [
        'verified',
        HasFileFilter,
        HasFilePageOffsetFilter,
        HasPageNumber,
        ImpreciseDateFilter,
        'hidden',
        'attributees',
        'polymorphic_ctype'
    ]
    readonly_fields = ['db_string']
    search_fields = models.Source.searchable_fields
    ordering = (
        'date',
        'creators',
        'polymorphic_ctype'
    )
    inlines = [AttributeesInline, ContainersInline, ContainedSourcesInline, RelatedInline]
    autocomplete_fields = ['file', 'location']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'database_string' in fields:
            fields.remove('database_string')
            fields.insert(0, 'database_string')


class ChildModelAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, Admin):
    base_model = models.Source
    list_display = [
        'string',
        'detail_link',
        'description',
        'date_string'
    ]
    list_filter = ['verified', 'attributees']
    readonly_fields = ['db_string']
    search_fields = ['db_string']
    ordering = ['date', 'creators']
    inlines = SourceAdmin.inlines
    autocomplete_fields = SourceAdmin.autocomplete_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('title', 'creators', 'db_string'):
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
    list_display = ['__str__', 'description', 'type2']
    search_fields = ['name']
    list_filter = ['type2']


class ArticleAdmin(ChildModelAdmin):
    list_display = ['string', 'publication', 'description', 'date_string']
    autocomplete_fields = ChildModelAdmin.autocomplete_fields + ['publication']


class ArticlesInline(StackedInline):
    model = models.Article
    extra = 1


class SpeechAdmin(ChildModelAdmin):
    list_display = ['string', 'type2', 'location', 'date_string']
    search_fields = ['db_string', 'location__name']


class CollectionAdmin(Admin):
    search_fields = ['name', 'repository__name', 'repository__location__name']
    autocomplete_fields = ['repository']


class DocumentAdmin(ChildModelAdmin):
    search_fields = ChildModelAdmin.search_fields
    autocomplete_fields = ['collection', 'file']


class RepositoryAdmin(Admin):
    search_fields = ['name', 'location__name']
    autocomplete_fields = ['location']


class SourcesInline(TabularInline):
    model = models.Source
    extra = 0
    fields = ['verified', 'hidden', 'date_is_circa', 'creators', 'url', 'date', 'publication_date']


admin_site.register(models.Source, SourceAdmin)

admin_site.register(models.Article, ArticleAdmin)

admin_site.register(models.Speech, SpeechAdmin)

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
