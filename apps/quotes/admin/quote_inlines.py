"""Admin for the quotes app."""

import re
from typing import Optional

from admin import GenericTabularInline, TabularInline
from modularhistory.constants.misc import OCCURRENCE_CT_ID
from apps.quotes import models


class AttributeesInline(TabularInline):
    """Inline admin for a quote's attributees."""

    model = models.QuoteAttribution
    autocomplete_fields = ['attributee']

    sortable_field_name = 'position'

    def get_extra(
        self, request, model_instance: Optional[models.Quote] = None, **kwargs
    ):
        """TODO: add docstring."""
        if model_instance and model_instance.attributees.count():
            return 0
        return 1


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
        ct_id = OCCURRENCE_CT_ID
        return models.QuoteRelation.objects.filter(quote_id=pk, content_type_id=ct_id)

    def get_extra(self, request, model_instance=None, **kwargs):
        """Return the number of extra/blank input rows to display."""
        if len(self.get_queryset(request)):
            return 0
        return 1
