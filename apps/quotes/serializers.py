"""Serializers for the entities app."""

from typing import TYPE_CHECKING

import serpy
from django.template.defaultfilters import truncatechars_html

from core.models.module import ModuleSerializer

if TYPE_CHECKING:
    from apps.quotes.models.quote import Quote


class QuoteSerializer(ModuleSerializer):
    """Serializer for quotes."""

    bite = serpy.MethodField()
    html = serpy.StrField()
    attributee_html = serpy.StrField(attr='attributee_html')
    attributee_string = serpy.StrField(attr='attributee_string')
    dateString = serpy.StrField(attr='date_string')
    cachedImages = serpy.Field(attr='cached_images')
    primaryImage = serpy.Field(attr='primary_image')
    cachedCitations = serpy.Field(attr='cached_citations')

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'quotes.quote'

    def get_bite(self, instance: 'Quote') -> str:
        """Return the user-facing bite HTML."""
        # Set `bite` to truncated text if it does not exist.
        return instance.bite if instance.bite else truncatechars_html(instance.text, 150)
