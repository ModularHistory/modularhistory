from typing import List

from admin import ModelAdmin, StackedInline, admin_site
from sources import models
from sources.admin.source_admin import SourceAdmin
from sources.admin.source_filters import AttributeeFilter


class TextualSourceAdmin(SourceAdmin):
    """Admin for textual sources."""

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

    def get_fields(self, request, model_instance=None):
        """TODO: add docstring."""
        fields: List = list(super().get_fields(request, model_instance))
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


class ArticleAdmin(TextualSourceAdmin):
    """TODO: add docstring."""

    list_display = ['pk', 'html', 'publication', 'description', 'date_string']
    autocomplete_fields = TextualSourceAdmin.autocomplete_fields + ['publication']
    ordering = TextualSourceAdmin.ordering


class BookAdmin(TextualSourceAdmin):
    """TODO: add docstring."""

    list_display = TextualSourceAdmin.list_display
    autocomplete_fields = TextualSourceAdmin.autocomplete_fields + ['original_edition']
    ordering = TextualSourceAdmin.ordering


class ArticlesInline(StackedInline):
    """TODO: add docstring."""

    model = models.Article
    extra = 1


class CollectionAdmin(ModelAdmin):
    """TODO: add docstring."""

    search_fields = ['name', 'repository__name', 'repository__location__name']
    autocomplete_fields = ['repository']


class DocumentAdmin(TextualSourceAdmin):
    """TODO: add docstring."""

    autocomplete_fields = ['collection', 'db_file']


class RepositoryAdmin(ModelAdmin):
    """TODO: add docstring."""

    search_fields = ['name', 'location__name']
    autocomplete_fields = ['location']


admin_site.register(models.Article, ArticleAdmin)
admin_site.register(models.Book, BookAdmin)

admin_site.register(models.Publication, PublicationAdmin)

admin_site.register(models.Document, DocumentAdmin)
admin_site.register(models.Letter, DocumentAdmin)
admin_site.register(models.Collection, CollectionAdmin)
admin_site.register(models.Repository, RepositoryAdmin)

admin_site.register(models.JournalEntry, TextualSourceAdmin)

child_models = (
    models.Chapter,
    models.Piece,
    models.Documentary,
    models.WebPage,
    models.Affidavit
)

for child in child_models:
    admin_site.register(child, TextualSourceAdmin)
