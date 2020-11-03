"""Serializers for the entities app."""

import serpy
from typing import TYPE_CHECKING
from modularhistory.models.searchable_model import SearchableModelSerializer

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

    def get_bite(self, instance: 'Quote'):
        return instance.bite.html
