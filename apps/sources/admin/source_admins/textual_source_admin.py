from typing import List

from admin import admin_site
from apps.sources import models
from apps.sources.admin.filters import AttributeeFilter
from apps.sources.admin.source_admins.source_admin import SourceAdmin, SourceForm


class TextualSourceForm(SourceForm):
    """Form for adding/updating books."""

    model = models.TextualSource

    class Meta:
        model = models.TextualSource
        exclude = []


class TextualSourceAdmin(SourceAdmin):
    """Admin for textual sources."""

    form = TextualSourceForm
    list_display = ['pk', 'html', 'detail_link', 'date_string']
    list_filter = ['verified', AttributeeFilter]

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the admin."""
        fields: List = list(super().get_fields(request, model_instance))
        # Fields to display at the top, in order
        top_fields = ('full_string', 'creators', 'title')
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


admin_site.register(models.Piece, TextualSourceAdmin)
