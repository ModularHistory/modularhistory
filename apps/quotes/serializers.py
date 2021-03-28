"""Serializers for the entities app."""

from typing import TYPE_CHECKING

import serpy

from apps.search.models.searchable_model import SearchableModelSerializer
from django.template.defaultfilters import truncatechars_html

if TYPE_CHECKING:
    from apps.quotes.models import Quote


class QuoteSerializer(SearchableModelSerializer):
    """Serializer for quotes."""

    text = serpy.Field(attr='text.html', required=True)
    bite = serpy.MethodField()
    html = serpy.Field()
    truncated_html = serpy.MethodField()
    attributee_string = serpy.Field()
    has_multiple_attributees = serpy.BoolField()
    attributee_html = serpy.Field()
    date_html = serpy.Field()
    serialized_images = serpy.Field()
    primary_image = serpy.Field()
    serialized_citations = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'quotes.quote'

    def get_bite(self, instance: 'Quote') -> str:
        """Return the user-facing bite HTML."""
        # "bite" is set to truncated text if it does not exist
        # TODO: Add "truncated" field to model to distinguish true bites from auto bites
        return instance.bite.html if instance.bite else truncatechars_html(instance.text, 100)

    def get_truncated_html(self, instance: 'Quote') -> str:
        """Return truncated HTML content"""
        if instance.bite is not None:
            return truncatechars_html(instance.bite, 100)
        else:
            return truncatechars_html(instance.text, 100)
