from typing import List, Optional, TYPE_CHECKING

from admin import GenericTabularInline
from quotes import models

if TYPE_CHECKING:
    from modularhistory.models import ModelWithRelatedQuotes


class RelatedQuotesInline(GenericTabularInline):
    """TODO: add docstring."""

    model = models.QuoteRelation
    autocomplete_fields: List[str] = ['quote']
    readonly_fields: List[str] = ['quote_pk']

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(
        self,
        request,
        model_instance: Optional['ModelWithRelatedQuotes'] = None,
        **kwargs
    ):
        """TODO: add docstring."""
        if model_instance and model_instance.quote_relations.count():
            return 0
        return 1
