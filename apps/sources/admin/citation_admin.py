from typing import TYPE_CHECKING, Optional

from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from admin import GenericTabularInline, ModelAdmin, TabularInline, admin_site
from apps.sources import models

if TYPE_CHECKING:
    from apps.sources.models import ModelWithSources


class ContentTypeFilter(SimpleListFilter):
    """Filters citations by the content type of their related model instances."""

    title = 'content type'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        content_type_ids = (
            models.Citation.objects.all().values('content_type').distinct()
        )
        content_types = ContentType.objects.filter(id__in=content_type_ids)
        return [(f'{ct.app_label}.{ct.model}', f'{ct}') for ct in content_types]

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
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

    model = models.Citation

    list_display = ['pk', 'html', 'position', 'content_object', 'content_type']
    search_fields = ['source__full_string']
    list_filter = [ContentTypeFilter]
    list_per_page = 10

    def get_queryset(self, request) -> 'QuerySet[models.Citation]':
        """
        Return the queryset of citations to be displayed in the admin.

        https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_queryset
        """
        qs = (
            models.Citation.objects.all()
            .select_related('source', f'source__{models.Source.FieldNames.file}')
            .prefetch_related('content_object', 'pages')
        )
        ordering = self.get_ordering(request)
        if ordering and ordering != models.Citation.get_meta().ordering:
            qs = qs.order_by(*ordering)
        return qs


class PagesInline(TabularInline):
    """Inline admin for a citation's page numbers/ranges."""

    model = models.PageRange
    verbose_name = 'page range'
    verbose_name_plural = 'pages'
    exclude = ['computations']

    def get_extra(
        self, request, model_instance: Optional[models.Citation] = None, **kwargs
    ):
        """Return the number of extra/blank rows to include."""
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
    exclude = ['computations']

    inlines = [PagesInline]

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(
        self, request, model_instance: Optional['ModelWithSources'] = None, **kwargs
    ):
        """Return the number of extra/blank rows to include."""
        if model_instance and model_instance.citations.count():
            return 0
        return 1

    def get_queryset(self, request) -> QuerySet:
        """Return the queryset of citations to display in an inline admin."""
        return super().get_queryset(request).prefetch_related('pages')


admin_site.register(models.Citation, CitationAdmin)
