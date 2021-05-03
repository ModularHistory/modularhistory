"""Serializers for the entities app."""

from typing import TYPE_CHECKING

import serpy
from django.template.defaultfilters import truncatechars_html

from apps.search.models.searchable_model import SearchableModelSerializer

if TYPE_CHECKING:
    from apps.quotes.models import Quote


class QuoteSerializer(SearchableModelSerializer):
    """Serializer for quotes."""

    bite = serpy.MethodField()
    html = serpy.Field()
    has_multiple_attributees = serpy.BoolField()
    attributeeHtml = serpy.Field(attr='attributee_html')
    attributeeString = serpy.Field(attr='attributee_string')
    dateHtml = serpy.Field(attr='date_html')
    serializedImages = serpy.Field(attr='serialized_images')
    primaryImage = serpy.Field(attr='primary_image')
    serializedCitations = serpy.Field(attr='serialized_citations')

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'quotes.quote'

    def get_bite(self, instance: 'Quote') -> str:
        """Return the user-facing bite HTML."""
        # Set `bite`` to truncated text if it does not exist.
        return (
            instance.bite.html
            if instance.bite
            else truncatechars_html(instance.text, 150)
        )
