from django.contrib.admin import SimpleListFilter

from admin.model_admin import ModelAdmin, admin_site
from apps.sources import models
from apps.sources.admin.source_admins.source_admin import SourcesInline
from modularhistory.constants.strings import NO, YES

PAGE_OFFSET_FIELD = 'page_offset'


class PdfFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'is PDF'
    parameter_name = 'is_pdf'

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        if self.value() == YES:
            return queryset.filter(name__icontains='pdf')
        if self.value() == NO:
            return queryset.exclude(name__icontains='pdf')


class SourceFileAdmin(ModelAdmin):
    """Admin for source files."""

    list_display = ['name', PAGE_OFFSET_FIELD, 'link', 'uploaded_at', 'id']
    search_fields = ['file', 'name']
    inlines = [SourcesInline]
    list_filter = [PdfFilter]
    ordering = ['name', 'uploaded_at', 'id']

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the admin."""
        fields = super().get_fields(request, model_instance)
        if fields and PAGE_OFFSET_FIELD in fields:
            fields.remove(PAGE_OFFSET_FIELD)
            fields.append(PAGE_OFFSET_FIELD)
        return fields


admin_site.register(models.SourceFile, SourceFileAdmin)
