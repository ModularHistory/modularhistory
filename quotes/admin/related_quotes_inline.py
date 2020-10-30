from typing import List

from admin import GenericTabularInline
from quotes import models


class RelatedQuotesInline(GenericTabularInline):
    """TODO: add docstring."""

    model = models.QuoteRelation
    autocomplete_fields: List[str] = ['quote']
    readonly_fields: List[str] = ['quote_pk']
    extra = 0

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'
