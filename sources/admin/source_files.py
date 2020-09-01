from django.contrib.admin import SimpleListFilter

from history.admin import admin_site, Admin
from .admin import SourcesInline
from .. import models


class PdfFilter(SimpleListFilter):
    title = 'is PDF'
    parameter_name = 'is_pdf'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(name__icontains='pdf')
        if self.value() == 'No':
            return queryset.exclude(name__icontains='pdf')


class SourceFileAdmin(Admin):
    list_display = ['__str__', 'name', 'page_offset', 'link']
    search_fields = ['file', 'name']
    inlines = [SourcesInline]
    list_filter = [PdfFilter]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if fields and 'page_offset' in fields:
            fields.remove('page_offset')
            fields.append('page_offset')
        return fields


admin_site.register(models.SourceFile, SourceFileAdmin)
