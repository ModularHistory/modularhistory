"""Admin for the quotes app."""


from apps.admin import TabularInline
from apps.quotes import models
from core.constants.content_types import ContentTypes, get_ct_id


class AttributeesInline(TabularInline):
    """Inline admin for a quote's attributees."""

    model = models.QuoteAttribution
    autocomplete_fields = ['attributee']

    sortable_field_name = 'position'


class BitesInline(TabularInline):
    """Inline admin for a quote's bites."""

    model = models.QuoteBite
    extra = 0
