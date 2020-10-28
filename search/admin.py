from admin.model_admin import ModelAdmin, admin_site
from search import models


class SearchAdmin(ModelAdmin):
    """Admin for user searches."""

    list_display = ['pk']


admin_site.register(models.Search, SearchAdmin)
