from django.contrib.admin import SimpleListFilter

from admin.admin import admin_site, Admin
from sources import models
from sources.admin.sources_admin import SourcesInline


class PdfFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'is PDF'
    parameter_name = 'is_pdf'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.filter(name__icontains='pdf')
        if self.value() == 'No':
            return queryset.exclude(name__icontains='pdf')


class SourceFileAdmin(Admin):
    """TODO: add docstring."""

    list_display = ['__str__', 'name', 'page_offset', 'link']
    search_fields = ['file', 'name']
    inlines = [SourcesInline]
    list_filter = [PdfFilter]

    def get_fields(self, request, obj=None):
        """TODO: add docstring."""
        fields = super().get_fields(request, obj)
        if fields and 'page_offset' in fields:
            fields.remove('page_offset')
            fields.append('page_offset')
        return fields


admin_site.register(models.SourceFile, SourceFileAdmin)
