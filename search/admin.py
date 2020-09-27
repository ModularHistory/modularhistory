from admin.admin import Admin, admin_site
from search import models


class SearchAdmin(Admin):
    """Admin for user searches."""

    list_display = [
        'pk',
    ]
    # list_filter = []
    # search_fields = models.Quote.searchable_fields
    # ordering = ['date']
    # autocomplete_fields = []
    # readonly_fields = ['citation_html']
    # inlines = []


admin_site.register(models.Search, SearchAdmin)
