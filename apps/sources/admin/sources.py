import re
from typing import Iterable, List, Tuple, Type, Union

from django.contrib.admin.filters import ListFilter
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from apps.admin import TabularInline, admin_site
from apps.search.admin import SearchableModelAdmin
from apps.sources import models
from apps.sources.admin.filters import AttributeeFilter, HasContainerFilter
from apps.sources.admin.filters.simple_filters import SourceTypeFilter
from apps.sources.admin.inlines import (
    AttributeesInline,
    ContainedSourcesInline,
    ContainersInline,
    RelatedInline,
)


class SourceAdmin(PolymorphicParentModelAdmin, SearchableModelAdmin):
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
        models.Section,
        models.Speech,
        models.Webpage,
    )

    list_display = [
        'pk',
        'escaped_citation_html',
        'attributee_string',
        'date_string',
        'slug',
        'ctype_name',
    ]
    list_filter: List[Union[str, Type[ListFilter]]] = [
        'verified',
        HasContainerFilter,
        # HasFileFilter,
        # HasFilePageOffsetFilter,
        # ImpreciseDateFilter,
        'hidden',
        AttributeeFilter,
        SourceTypeFilter,
    ]
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10
    ordering = ['date', 'citation_string']
    search_fields = base_model.searchable_fields

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet, search_term: str
    ) -> Tuple[QuerySet, bool]:
        """Return source instances matching the supplied search term."""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        # If the request comes from the admin edit page for a model instance,
        # exclude the model instance from the search results. This prevents
        # inline admins from displaying an unwanted value in an autocomplete
        # field or, in the worst-case scenario, letting an admin errantly
        # create a relationship between a model instance and itself.
        referer = request.META.get('HTTP_REFERER') or ''
        match = re.match(r'.+/(\d+)/change', referer)
        if match:
            pk = int(match.group(1))
            queryset = queryset.exclude(pk=pk)
        return queryset, use_distinct

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the source admin form."""
        fields = list(super().get_fields(request, model_instance))
        return rearrange_fields(fields)

    def get_queryset(self, request):
        """Return the queryset of sources to be displayed in the source admin."""
        return super().get_queryset(request).select_related('polymorphic_ctype')


class ChildSourceAdmin(PolymorphicChildModelAdmin, SearchableModelAdmin):
    """
    Admin for source models that inherit from the base `Source` model.

    Such source models (e.g., `Article`) must be registered with `ChildSourceAdmin`
    or with a custom admin that inherits from `ChildSourceAdmin`.
    """

    base_model = models.Source

    autocomplete_fields = ['file', 'location']
    exclude = [
        'citation_html',
        'citation_string',
    ]
    inlines = [
        AttributeesInline,
        ContainersInline,
        ContainedSourcesInline,
        RelatedInline,
    ]
    list_display = [field for field in SourceAdmin.list_display if field != 'ctype']
    # Without a hint, mypy seems unable to infer the type of `filter`
    # in the list comprehension.
    filter: Union[str, Type[ListFilter]]
    list_filter = [
        filter for filter in SourceAdmin.list_filter if filter != SourceTypeFilter
    ]
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 15
    ordering = SourceAdmin.ordering
    readonly_fields = SearchableModelAdmin.readonly_fields + [
        'escaped_citation_html',
        'attributee_html',
        'citation_string',
        'containment_html',
        'computations',
    ]
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as
    save_as = True
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_as_continue
    save_as_continue = True
    search_fields = base_model.searchable_fields

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the admin."""
        return rearrange_fields(super().get_fields(request, model_instance))


class TextualSourceAdmin(ChildSourceAdmin):
    """Admin for textual sources."""

    autocomplete_fields = ChildSourceAdmin.autocomplete_fields + ['original_edition']


class ArticleAdmin(TextualSourceAdmin):
    """Admin for articles."""

    autocomplete_fields = ChildSourceAdmin.autocomplete_fields + ['publication']


class SourcesInline(TabularInline):
    """Inline admin for sources."""

    model = models.Source
    extra = 0
    fields = [
        'verified',
        'hidden',
        'date_is_circa',
        'attributee_string',
        'url',
        'date',
        'publication_date',
    ]


def rearrange_fields(fields: Iterable[str]):
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


admin_site.register(models.Source, SourceAdmin)

admin_site.register(models.Affidavit, ChildSourceAdmin)
admin_site.register(models.Article, ArticleAdmin)
admin_site.register(models.Book, TextualSourceAdmin)
admin_site.register(models.Correspondence, ChildSourceAdmin)
admin_site.register(models.Document, ChildSourceAdmin)
admin_site.register(models.Film, ChildSourceAdmin)
admin_site.register(models.Interview, ChildSourceAdmin)
admin_site.register(models.Entry, ChildSourceAdmin)
admin_site.register(models.Piece, ChildSourceAdmin)
admin_site.register(models.Section, ChildSourceAdmin)
admin_site.register(models.Speech, ChildSourceAdmin)
admin_site.register(models.Webpage, ChildSourceAdmin)
