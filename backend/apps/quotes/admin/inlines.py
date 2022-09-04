"""Admin for the quotes app."""


from apps.admin import TabularInline
from apps.quotes import models


class AttributeesInline(TabularInline):
    """Inline admin for a quote's attributees."""

    model = models.QuoteAttribution
    autocomplete_fields = ['attributee']

    sortable_field_name = 'position'
