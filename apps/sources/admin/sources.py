from typing import Iterable

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


def rearrange_fields(fields: Iterable[str]):
    """Return reordered fields to be displayed in the admin."""
    # Fields to display at the top, in order
    top_fields = (
        'escaped_citation_html',
        'citation_string',
        'attributee_string',
        'title',
        'slug',
    )
    # Fields to display at the bottom, in order
    bottom_fields = (
        'volume',
        'number',
        'page_number',
        'end_page_number',
        'container',
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


class SourceAdmin(PolymorphicParentModelAdmin, SearchableModelAdmin):

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
    list_filter = [
        'verified',
        HasContainerFilter,
        # HasFileFilter,
        # HasFilePageOffsetFilter,
        # ImpreciseDateFilter,
        models.Source.FieldNames.hidden,
        AttributeeFilter,
        SourceTypeFilter,
    ]
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10
    ordering = ['date', 'citation_string']
    search_fields = base_model.searchable_fields

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the admin."""
        fields: list(super().get_fields(request, model_instance))
        return rearrange_fields(fields)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('polymorphic_ctype')


class ChildSourceAdmin(PolymorphicChildModelAdmin, SearchableModelAdmin):
    """ Base admin class for all child models """

    base_model = models.Source

    # # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # # the additional fields of the child models are automatically added to the admin form.
    # base_form = ...
    # base_fieldsets = ...

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
    list_filter = [
        filter for filter in SourceAdmin.list_filter if filter != SourceTypeFilter
    ]
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 15
    ordering = SourceAdmin.ordering
    readonly_fields = SearchableModelAdmin.readonly_fields + [
        'escaped_citation_html',
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


class SourcesInline(TabularInline):
    """Inline admin for sources."""

    model = models.Source
    extra = 0
    fields = [
        'verified',
        'hidden',
        'date_is_circa',
        'creators',
        'url',
        'date',
        'publication_date',
    ]


admin_site.register(models.Source, SourceAdmin)

admin_site.register(models.Affidavit, ChildSourceAdmin)
admin_site.register(models.Article, ChildSourceAdmin)
admin_site.register(models.Book, ChildSourceAdmin)
admin_site.register(models.Correspondence, ChildSourceAdmin)
admin_site.register(models.Document, ChildSourceAdmin)
admin_site.register(models.Film, ChildSourceAdmin)
admin_site.register(models.Interview, ChildSourceAdmin)
admin_site.register(models.Entry, ChildSourceAdmin)
admin_site.register(models.Piece, ChildSourceAdmin)
admin_site.register(models.Section, ChildSourceAdmin)
admin_site.register(models.Speech, ChildSourceAdmin)
admin_site.register(models.Webpage, ChildSourceAdmin)
