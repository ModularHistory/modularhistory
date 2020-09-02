from history.admin import GenericTabularInline
from .. import models
from typing import List


class RelatedQuotesInline(GenericTabularInline):
    """TODO: add docstring."""

    model = models.QuoteRelation
    autocomplete_fields: List[str] = ['quote']
    readonly_fields: List[str] = ['quote_pk']
    # verbose_name = 'citation'
    # verbose_name_plural = 'citations'

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(self, request, obj=None, **kwargs):
        """TODO: add docstring."""
        if obj and obj.quote_relations.count():
            return 0
        return 1
