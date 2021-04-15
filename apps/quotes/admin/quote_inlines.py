"""Admin for the quotes app."""

import re

from apps.admin import GenericTabularInline, TabularInline
from apps.quotes import models
from modularhistory.constants.content_types import ContentTypes, get_ct_id


class AttributeesInline(TabularInline):
    """Inline admin for a quote's attributees."""

    model = models.QuoteAttribution
    autocomplete_fields = ['attributee']

    sortable_field_name = 'position'


class BitesInline(TabularInline):
    """Inline admin for a quote's bites."""

    model = models.QuoteBite
    extra = 0


# TODO: try to get this reverse relationship working
class OccurrencesInline(GenericTabularInline):
    """Inline admin for a quote's related occurrences."""

    model = models.QuoteRelation
    verbose_name = 'occurrence'
    verbose_name_plural = 'occurrences'

    def get_queryset(self, request):
        """Return the filtered queryset."""
        pk = re.search(r'/(\d+)/', request.path).group(1)
        ct_id = get_ct_id(ContentTypes.occurrence)
        return models.QuoteRelation.objects.filter(quote_id=pk, content_type_id=ct_id)
