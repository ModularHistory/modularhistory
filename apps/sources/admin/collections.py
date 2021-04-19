from apps.admin import ModelAdmin, admin_site
from apps.sources import models


class CollectionAdmin(ModelAdmin):
    """Admin for document collections."""

    search_fields = ['name', 'repository__name', 'repository__location__name']
    autocomplete_fields = ['repository']


class RepositoryAdmin(ModelAdmin):
    """Admin for document repositories."""

    search_fields = ['name', 'location__name']
    autocomplete_fields = ['location']


admin_site.register(models.Collection, CollectionAdmin)
admin_site.register(models.Repository, RepositoryAdmin)
