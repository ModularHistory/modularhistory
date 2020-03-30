from admin import admin_site, Admin
from .admin import SourcesInline
from .. import models


class SourceFileAdmin(Admin):
    list_display = ['__str__', 'name', 'page_offset']
    search_fields = ['_file']
    inlines = [SourcesInline]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if fields and 'page_offset' in fields:
            fields.remove('page_offset')
            fields.append('page_offset')
        return fields


admin_site.register(models.SourceFile, SourceFileAdmin)
