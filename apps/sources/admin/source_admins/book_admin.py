from admin import admin_site
from apps.sources import models
from apps.sources.admin.source_admins.textual_source_admin import (
    TextualSourceAdmin,
    TextualSourceForm,
)


class BookForm(TextualSourceForm):
    """Form for adding/updating books."""

    model = models.Book

    class Meta:
        model = models.Book
        exclude = model.inapplicable_fields


class BookAdmin(TextualSourceAdmin):
    """Admin for books."""

    form = BookForm
    list_display = TextualSourceAdmin.list_display
    autocomplete_fields = TextualSourceAdmin.autocomplete_fields + ['original_edition']
    ordering = TextualSourceAdmin.ordering


admin_site.register(models.Book, BookAdmin)
admin_site.register(models.Chapter, TextualSourceAdmin)
