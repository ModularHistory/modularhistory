from typing import Optional, TYPE_CHECKING

from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType

from admin import GenericTabularInline, ModelAdmin, TabularInline, admin_site
from sources import models

if TYPE_CHECKING:
    from modularhistory.models import ModelWithSources


class ContentTypeFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'content type'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        """Returns an iterable of tuples (value, verbose value)."""
        content_type_ids = models.Citation.objects.all().values('content_type').distinct()
        content_types = ContentType.objects.filter(id__in=content_type_ids)
        return [(f'{ct.app_label}.{ct.model}', f'{ct}') for ct in content_types]

    def queryset(self, request, queryset):
        """Returns the filtered queryset."""
        content_type = self.value()
        if not content_type:
            return queryset
        if '.' in content_type:
            app_name, model_name = content_type.split('.')
            ct = ContentType.objects.get(app_label=app_name, model=model_name)
            return queryset.filter(content_type=ct)
        return queryset


class CitationAdmin(ModelAdmin):
    """Admin for citations."""
    list_display = ['pk', 'html', 'position', 'content_object', 'content_type']
    search_fields = ['source__db_string']
    list_filter = [ContentTypeFilter]


class PagesInline(TabularInline):
    """Inline admin for a citation's page numbers/ranges."""

    model = models.PageRange
    verbose_name = 'page range'
    verbose_name_plural = 'pages'

    def get_extra(self, request, model_instance: Optional[models.Citation] = None, **kwargs):
        """TODO: add docstring."""
        if model_instance and model_instance.pages.count():
            return 0
        return 1


class CitationsInline(GenericTabularInline):
    """Inline admin for citations."""

    model = models.Citation
    autocomplete_fields = ['source']
    readonly_fields = ['pk']
    verbose_name = 'citation'
    verbose_name_plural = 'citations'

    inlines = [PagesInline]

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(self, request, model_instance: Optional['ModelWithSources'] = None, **kwargs):
        """TODO: add docstring."""
        if model_instance and model_instance.citations.count():
            return 0
        return 1


admin_site.register(models.Citation, CitationAdmin)
