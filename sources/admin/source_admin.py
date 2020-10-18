from typing import List

from django.urls import path

from admin import ModelAdmin, SearchableModelAdmin, StackedInline, TabularInline, admin_site
from entities.views import AttributeeSearchView
from sources import models
from sources.admin.source_filters import (
    AttributeeFilter,
    HasContainerFilter,
    HasFileFilter,
    HasFilePageOffsetFilter,
    HasPageNumber,
    ImpreciseDateFilter,
    TypeFilter
)
from sources.admin.source_inlines import AttributeesInline, ContainedSourcesInline, ContainersInline, RelatedInline
from sources.models import Source


class SourceAdmin(SearchableModelAdmin):
    """TODO: add docstring."""

    model = Source
    list_display = [
        'pk',
        'html',
        'date_string',
        'location',
        'admin_file_link',
        'type'
    ]
    list_filter = [
        'verified',
        HasContainerFilter,
        HasFileFilter,
        HasFilePageOffsetFilter,
        HasPageNumber,
        ImpreciseDateFilter,
        'hidden',
        AttributeeFilter,
        TypeFilter
    ]
    readonly_fields = SearchableModelAdmin.readonly_fields + ['db_string']
    search_fields = Source.searchable_fields
    ordering = ['date', 'db_string']
    inlines = [AttributeesInline, ContainersInline, ContainedSourcesInline, RelatedInline]
    autocomplete_fields = ['db_file', 'location']

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 20

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as
    save_as = True

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as_continue
    save_as_continue = True

    def get_fields(self, request, obj=None):
        """TODO: add docstring."""
        fields = list(super().get_fields(request, obj))
        if 'database_string' in fields:
            fields.remove('database_string')
            fields.insert(0, 'database_string')
        return fields

    def get_urls(self):
        """TODO: add docstring."""
        urls = super().get_urls()
        additional_urls = [
            path(
                'attributee_search/',
                self.admin_site.admin_view(AttributeeSearchView.as_view(model_admin=self)),
                name='attributee_search'
            ),
        ]
        return additional_urls + urls


class ChildModelAdmin(SourceAdmin):
    """TODO: add docstring."""

    list_display = [
        'pk',
        'html',
        'detail_link',
        'date_string'
    ]
    list_filter = [
        'verified',
        AttributeeFilter
    ]

    def get_fields(self, request, obj=None):
        """TODO: add docstring."""
        fields: List = list(super().get_fields(request, obj))
        # Fields to display at the top, in order
        top_fields = (
            'db_string',
            'creators',
            'title'
        )
        # Fields to display at the bottom, in order
        bottom_fields = (
            'volume',
            'number',
            'page_number',
            'end_page_number',
            'container',
            'description',
            'citations'
        )
        index: int = 0
        for field_name in top_fields:
            if field_name in fields:
                fields.remove(field_name)
                fields.insert(index, field_name)
                index += 1
        for field_name in bottom_fields:
            if field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields


class PublicationAdmin(ModelAdmin):
    """TODO: add docstring."""

    list_display = ['__str__', 'description']
    search_fields = ['name']


class ArticleAdmin(ChildModelAdmin):
    """TODO: add docstring."""

    list_display = ['pk', 'html', 'publication', 'description', 'date_string']
    autocomplete_fields = ChildModelAdmin.autocomplete_fields + ['publication']
    ordering = ChildModelAdmin.ordering


class BookAdmin(ChildModelAdmin):
    """TODO: add docstring."""

    list_display = ChildModelAdmin.list_display
    autocomplete_fields = ChildModelAdmin.autocomplete_fields + ['original_edition']
    ordering = ChildModelAdmin.ordering


class ArticlesInline(StackedInline):
    """TODO: add docstring."""

    model = models.Article
    extra = 1


class SpeechAdmin(ChildModelAdmin):
    """TODO: add docstring."""

    list_display = ['string', 'location', 'date_string']
    search_fields = ['db_string', 'location__name']


class CollectionAdmin(ModelAdmin):
    """TODO: add docstring."""

    search_fields = ['name', 'repository__name', 'repository__location__name']
    autocomplete_fields = ['repository']


class DocumentAdmin(ChildModelAdmin):
    """TODO: add docstring."""

    autocomplete_fields = ['collection', 'db_file']


class RepositoryAdmin(ModelAdmin):
    """TODO: add docstring."""

    search_fields = ['name', 'location__name']
    autocomplete_fields = ['location']


class SourcesInline(TabularInline):
    """TODO: add docstring."""

    model = Source
    extra = 0
    fields = ['verified', 'hidden', 'date_is_circa', 'creators', 'url', 'date', 'publication_date']


admin_site.register(Source, SourceAdmin)

admin_site.register(models.Article, ArticleAdmin)
admin_site.register(models.Book, BookAdmin)
admin_site.register(models.Speech, SpeechAdmin)

admin_site.register(models.Publication, PublicationAdmin)

admin_site.register(models.Document, DocumentAdmin)
admin_site.register(models.Letter, DocumentAdmin)
admin_site.register(models.Collection, CollectionAdmin)
admin_site.register(models.Repository, RepositoryAdmin)

admin_site.register(models.JournalEntry, ChildModelAdmin)

child_models = (
    models.Chapter,
    models.Interview,
    models.Piece,
    models.Documentary,
    models.WebPage,
    models.Affidavit
)

for child in child_models:
    admin_site.register(child, ChildModelAdmin)
