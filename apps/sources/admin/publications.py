from apps.admin import ExtendedModelAdmin, StackedInline, admin_site
from apps.sources import models


class PublicationAdmin(ExtendedModelAdmin):
    """Admin for publications."""

    list_display = ['__str__', 'description']
    search_fields = ['name']


class ArticlesInline(StackedInline):
    """Inline admin for articles."""

    model = models.Article
    extra = 1


admin_site.register(models.Publication, PublicationAdmin)
admin_site.register(models.Journal, PublicationAdmin)
admin_site.register(models.Newspaper, PublicationAdmin)
admin_site.register(models.Magazine, PublicationAdmin)
admin_site.register(models.Website, PublicationAdmin)
