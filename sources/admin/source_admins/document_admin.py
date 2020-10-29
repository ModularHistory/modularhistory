from admin import ModelAdmin, admin_site
from sources import models
from sources.admin.source_admins.textual_source_admin import TextualSourceAdmin, TextualSourceForm


class CollectionAdmin(ModelAdmin):
    """Admin for document collections."""

    search_fields = ['name', 'repository__name', 'repository__location__name']
    autocomplete_fields = ['repository']


class DocumentForm(TextualSourceForm):
    """Form for adding/updating books."""

    model = models.Document

    class Meta:
        model = models.Document
        exclude = model.inapplicable_fields


class DocumentAdmin(TextualSourceAdmin):
    """Admin for documents."""

    form = DocumentForm
    autocomplete_fields = ['collection', 'db_file']


class RepositoryAdmin(ModelAdmin):
    """Admin for document repositories."""

    search_fields = ['name', 'location__name']
    autocomplete_fields = ['location']


admin_site.register(models.Collection, CollectionAdmin)
admin_site.register(models.Document, DocumentAdmin)
admin_site.register(models.JournalEntry, TextualSourceAdmin)
admin_site.register(models.Letter, DocumentAdmin)
admin_site.register(models.Repository, RepositoryAdmin)
admin_site.register(models.Affidavit, TextualSourceAdmin)
