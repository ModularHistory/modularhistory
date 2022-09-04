from typing import TYPE_CHECKING, Optional, Sequence, Union

from django.contrib.admin.filters import ListFilter
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from apps.admin.admin_site import admin_site
from apps.admin.inlines import StackedInline
from apps.search.admin import SearchableModelAdmin
from apps.sources import models
from apps.sources.admin.filters import AttributeeFilter, HasContainerFilter
from apps.sources.admin.filters.simple_filters import SourceTypeFilter
from apps.sources.admin.inlines import (
    AttributeesInline,
    ContainedSourcesInline,
    ContainersInline,
)

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet
    from django.http.request import HttpRequest


class AbstractSourceAdmin(SearchableModelAdmin):
    """Abstract base admin for PolymorphicSourceAdmin and SourceAdmin."""

    exclude = SearchableModelAdmin.exclude + [
        'attributees',
        'containers',
        'related_entities',
        'images',
        'locations',
        'citation_html',
        'citation_string',
    ]
    inlines = [
        AttributeesInline,
        ContainersInline,
        ContainedSourcesInline,
    ]
    list_display = [
        'slug',
        'escaped_citation_html',
        'attributee_string',
        'date_string',
    ]
    list_filter = [
        'verified',
        HasContainerFilter,
        # HasFileFilter,
        # HasFilePageOffsetFilter,
        # ImpreciseDateFilter,
        AttributeeFilter,
        SourceTypeFilter,
    ]
    ordering = ['date', 'citation_string']
    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10
    readonly_fields = SearchableModelAdmin.readonly_fields + [
        'escaped_citation_html',
        'attributee_html',
        'citation_string',
        'containment_html',
        'href',
        'cache',
    ]
    search_fields = models.Source.searchable_fields


class PolymorphicSourceAdmin(PolymorphicParentModelAdmin, AbstractSourceAdmin):
    """
    Admin for all sources, accessible at http://localhost/admin/sources/source/.

    This admin is not used for editing individual source instances;
    editing of individual model instances is delegated to `ChildSourceAdmin`
    or one of its subclasses.
    """

    base_model = models.Source
    child_models = (
        models.Affidavit,
        models.Article,
        models.Book,
        models.Correspondence,
        models.Document,
        models.Film,
        models.Interview,
        models.Entry,
        models.Piece,
        models.Report,
        models.Section,
        models.Speech,
        models.Webpage,
    )
    list_display = AbstractSourceAdmin.list_display + ['ctype_name']
    list_filter: list[Union[str, type[ListFilter]]] = [
        SourceTypeFilter,
        *AbstractSourceAdmin.list_filter,
    ]
    ordering = AbstractSourceAdmin.ordering
    readonly_fields = AbstractSourceAdmin.readonly_fields

    def get_search_results(
        self, request: 'HttpRequest', queryset: 'QuerySet', search_term: str
    ) -> tuple['QuerySet', bool]:
        """Return source instances matching the supplied search term."""
        queryset = queryset.non_polymorphic()
        return AbstractSourceAdmin.get_search_results(self, request, queryset, search_term)

    def get_queryset(self, request: 'HttpRequest') -> 'QuerySet':
        """Return the queryset of sources to be displayed in the source admin."""
        return super().get_queryset(request).select_related('polymorphic_ctype')


class SourceAdmin(PolymorphicChildModelAdmin, SearchableModelAdmin):
    """
    Admin for source models that inherit from the base `Source` model.

    Such source models (e.g., `Article`) must be registered with `ChildSourceAdmin`
    or with a custom admin that inherits from `ChildSourceAdmin`.
    """

    base_model = models.Source

    autocomplete_fields = ['file', 'location', 'release', 'original']
    exclude = AbstractSourceAdmin.exclude
    inlines = AbstractSourceAdmin.inlines
    list_display = AbstractSourceAdmin.list_display
    # Without a hint, mypy seems unable to infer the type of `filter` in list comprehensions.
    filter: Union[str, type[ListFilter]]
    list_filter = AbstractSourceAdmin.list_filter
    list_per_page = 15
    readonly_fields = AbstractSourceAdmin.readonly_fields
    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as
    save_as = True
    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as_continue
    save_as_continue = True
    search_fields = base_model.searchable_fields

    def get_fields(
        self, request: 'HttpRequest', model_instance: Optional['Model'] = None
    ) -> Sequence[str]:
        """Return reordered fields to be displayed in the admin."""
        return rearrange_fields(super().get_fields(request, model_instance))


class TextualSourceAdmin(SourceAdmin):
    """Admin for textual sources."""

    autocomplete_fields = SourceAdmin.autocomplete_fields


class ArticleAdmin(TextualSourceAdmin):
    """Admin for articles."""

    model = models.Article

    autocomplete_fields = SourceAdmin.autocomplete_fields + ['publication']


class SectionAdmin(TextualSourceAdmin):
    """Admin for sections."""

    model = models.Section

    autocomplete_fields = [*TextualSourceAdmin.autocomplete_fields, 'work']


class SectionsInline(StackedInline):
    """Inline admin for sections."""

    model = models.Section

    fk_name = 'work'
    exclude = SourceAdmin.exclude + [
        'date',
        'end_date',
        'date_is_circa',
        'location',
        'release',
        'original',
    ]
    readonly_fields = SourceAdmin.readonly_fields + ['source_ptr']
    extra = 0


class BookAdmin(TextualSourceAdmin):
    """Admin for books."""

    model = models.Book

    inlines = SourceAdmin.inlines + [SectionsInline]


class SourcesInline(StackedInline):
    """Inline admin for sources."""

    model = models.Source
    extra = 0
    fields = [
        'verified',
        'date_is_circa',
        'attributee_string',
        'url',
        'date',
        'publication_date',
    ]


def rearrange_fields(fields: Sequence[str]) -> Sequence[str]:
    """Return reordered fields to be displayed in the admin."""
    # Fields to display at the top, in order
    top_fields = (
        'escaped_citation_html',
        'citation_string',
        'attributee_string',
        'title',
        'slug',
        'date_is_circa',
        'date',
        'publication_date',
        'url',
        'file',
        'editors',
        'translator',
        'publisher',
    )
    # Fields to display at the bottom, in order
    bottom_fields = (
        'volume',
        'number',
        'page_number',
        'end_page_number',
        'description',
        'citations',
    )
    fields = list(fields)
    index: int = 0
    for top_field in top_fields:
        if top_field in fields:
            fields.remove(top_field)
            fields.insert(index, top_field)
            index += 1
    for bottom_field in bottom_fields:
        if bottom_field in fields:
            fields.remove(bottom_field)
            fields.append(bottom_field)
    return fields


admin_site.register(models.Source, PolymorphicSourceAdmin)

admin_site.register(models.Affidavit, SourceAdmin)
admin_site.register(models.Article, ArticleAdmin)
admin_site.register(models.Book, BookAdmin)
admin_site.register(models.Correspondence, SourceAdmin)
admin_site.register(models.Document, SourceAdmin)
admin_site.register(models.Film, SourceAdmin)
admin_site.register(models.Interview, SourceAdmin)
admin_site.register(models.Entry, SourceAdmin)
admin_site.register(models.Piece, SourceAdmin)
admin_site.register(models.Report, SourceAdmin)
admin_site.register(models.Section, SectionAdmin)
admin_site.register(models.Speech, SourceAdmin)
admin_site.register(models.Webpage, SourceAdmin)
