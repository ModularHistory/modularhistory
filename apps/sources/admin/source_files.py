from typing import TYPE_CHECKING, Optional

from django.contrib.admin import SimpleListFilter

from apps.admin.model_admin import ExtendedModelAdmin, admin_site
from apps.sources import models
from apps.sources.admin.sources import SourcesInline
from core.constants.strings import NO, YES

if TYPE_CHECKING:
    from django.contrib.admin.options import InlineModelAdmin
    from django.db.models import QuerySet
    from django.db.models.base import Model
    from django.http import HttpRequest

PAGE_OFFSET_FIELD = 'page_offset'


class PdfFilter(SimpleListFilter):
    """Filter for PDF source files."""

    title = 'is PDF'
    parameter_name = 'is_pdf'

    def lookups(self, request: 'HttpRequest', model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request: 'HttpRequest', queryset: 'QuerySet'):
        """Return the filtered queryset."""
        if self.value() == YES:
            return queryset.filter(name__icontains='pdf')
        if self.value() == NO:
            return queryset.exclude(name__icontains='pdf')


class SourceFileAdmin(ExtendedModelAdmin):
    """Admin for source files."""

    list_display = ['name', PAGE_OFFSET_FIELD, 'link', 'uploaded_at', 'id']
    search_fields = ['file', 'name']
    list_filter = [PdfFilter]
    ordering = ['name', 'uploaded_at', 'id']

    def get_fields(self, request: 'HttpRequest', model_instance: Optional['Model'] = None):
        """Return reordered fields to be displayed in the admin."""
        fields = list(super().get_fields(request, model_instance))
        if fields and PAGE_OFFSET_FIELD in fields:
            fields.remove(PAGE_OFFSET_FIELD)
            fields.append(PAGE_OFFSET_FIELD)
        return fields

    def get_inlines(
        self, request: 'HttpRequest', obj: Optional['Model'] = None
    ) -> list[type['InlineModelAdmin']]:
        """Return the inline admins to be displayed with the admin form."""
        inlines = super().get_inlines(request, obj=obj)
        referer = request.META.get('HTTP_REFERER') or ''
        if not referer.endswith('/add/'):
            inlines += [SourcesInline]
        return inlines


admin_site.register(models.SourceFile, SourceFileAdmin)
