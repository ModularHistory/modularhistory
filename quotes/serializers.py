"""Serializers for the entities app."""

from typing import TYPE_CHECKING

import serpy

from search.models.searchable_model import SearchableModelSerializer

if TYPE_CHECKING:
    from quotes.models import Quote


class QuoteSerializer(SearchableModelSerializer):
    """Serializer for quotes."""

    text = serpy.Field()
    bite = serpy.Field()
    html = serpy.Field()
    attributee_string = serpy.Field()
    has_multiple_attributees = serpy.BoolField()
    attributee_html = serpy.Field()
    date_html = serpy.Field()
    primary_image = serpy.Field()
    serialized_citations = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'quotes.quote'

    def get_bite(self, instance: 'Quote'):
        """Return the user-facing bite HTML."""
        return instance.bite.html
