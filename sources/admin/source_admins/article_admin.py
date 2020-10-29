from admin import ModelAdmin, StackedInline, admin_site
from sources import models
from sources.admin.source_admins.textual_source_admin import (
    TextualSourceAdmin,
    TextualSourceForm,
)


class PublicationAdmin(ModelAdmin):
    """Admin for publications."""

    list_display = ['__str__', 'description']
    search_fields = ['name']


class ArticleForm(TextualSourceForm):
    """Form for adding/editing articles."""

    model = models.Article

    class Meta:
        model = models.Article
        exclude = model.inapplicable_fields


class ArticleAdmin(TextualSourceAdmin):
    """Admin for articles."""

    form = ArticleForm
    list_display = ['pk', 'html', 'publication', 'description', 'date_string']
    autocomplete_fields = TextualSourceAdmin.autocomplete_fields + ['publication']
    ordering = TextualSourceAdmin.ordering


class ArticlesInline(StackedInline):
    """Inline admin for articles."""

    model = models.Article
    extra = 1


admin_site.register(models.Article, ArticleAdmin)
admin_site.register(models.Publication, PublicationAdmin)
admin_site.register(models.WebPage, TextualSourceAdmin)
