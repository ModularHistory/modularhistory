"""Serializers for the entities app."""


import serpy

from core.models.module import ModuleSerializer


class QuoteSerializer(ModuleSerializer):
    """Serializer for quotes."""

    bite = serpy.StrField()
    html = serpy.StrField()
    attributee_html = serpy.StrField()
    attributee_string = serpy.StrField()
    date_string = serpy.StrField()
    cached_images = serpy.Field()
    primary_image = serpy.Field()
    cached_citations = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'quotes.quote'
