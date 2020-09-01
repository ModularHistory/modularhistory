from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType

from history.admin import admin_site, Admin, TabularInline, GenericTabularInline
from .. import models


class ContentTypeFilter(SimpleListFilter):
    title = 'content type'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        content_types = models.Citation.objects.all().values('content_type').distinct()
        content_types = ContentType.objects.filter(id__in=content_types)
        return [
            (f'{ct.app_label}.{ct.model}', f'{ct}') for ct in content_types
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        if '.' in value:
            app_name, model_name = value.split('.')
            ct = ContentType.objects.get(app_label=app_name, model=model_name)
            return queryset.filter(content_type=ct)
        return queryset


class CitationAdmin(Admin):
    list_display = ['pk', 'html', 'position', 'content_object', 'content_type']
    search_fields = ['source__db_string']
    list_filter = [ContentTypeFilter]


class PagesInline(TabularInline):
    model = models.PageRange
    verbose_name = 'page range'
    verbose_name_plural = 'pages'

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.pages.count():
            return 0
        return 1


class CitationsInline(GenericTabularInline):
    model = models.Citation
    autocomplete_fields = ['source']
    readonly_fields = ['pk']
    verbose_name = 'citation'
    verbose_name_plural = 'citations'

    inlines = [PagesInline]

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.citations.count():
            return 0
        return 1


admin_site.register(models.Citation, CitationAdmin)
