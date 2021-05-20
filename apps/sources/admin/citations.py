from typing import TYPE_CHECKING, List, Optional, Type

from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from apps.admin import GenericTabularInline, ModelAdmin, admin_site
from apps.admin.inlines import TabularInline
from apps.sources import models

if TYPE_CHECKING:
    from apps.sources.models.model_with_sources import ModelWithSources


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

    autocomplete_fields = ['source']
    exclude = ['position']
    list_display = ['pk', 'html', 'content_object', 'content_type']
    list_filter = [ContentTypeFilter]
    list_per_page = 10
    ordering = ['pk']
    search_fields = ['source__citation_string']

    def get_queryset(self, request) -> 'QuerySet[models.Citation]':
        """
        Return the queryset of citations to be displayed in the admin.

        https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_queryset
        """
        qs = (
            models.Citation.objects.all()
            .select_related('source', 'source__file')
            .prefetch_related('content_object')
        )
        ordering = self.get_ordering(request)
        if ordering and ordering != models.Citation.get_meta().ordering:
            qs = qs.order_by(*ordering)
        return qs


class AbstractSourcesInline(TabularInline):
    """Inline admin for sources."""

    model: Type

    autocomplete_fields = ['source']
    # TODO: fix JSON widget so pages can be included in the inline editor
    exclude = ['cache', 'pages', 'citation_html']
    readonly_fields = ['escaped_citation_html', 'pk']
    verbose_name = 'citation'
    verbose_name_plural = 'sources'

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_fields(self, request, model_instance) -> List[str]:
        fields = super().get_fields(request, model_instance=model_instance)
        ordered_fields = ['citation_phrase']
        for field in ordered_fields:
            if field in fields:
                fields.remove(field)
                fields.insert(0, field)
        return fields


class CitationsInline(GenericTabularInline):
    """Inline admin for citations."""

    model = models.Citation

    autocomplete_fields = ['source']
    # TODO: fix JSON widget so pages can be included in the inline editor
    exclude = ['cache', 'pages']
    readonly_fields = ['pk']
    verbose_name = 'citation'
    verbose_name_plural = 'citations'

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
        return super().get_queryset(request)


admin_site.register(models.Citation, CitationAdmin)
