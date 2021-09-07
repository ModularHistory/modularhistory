"""Serializers for the entities app."""

from django.template.defaultfilters import truncatechars_html
from rest_framework import serializers

from apps.quotes.models.quote import Quote
from core.models.module import DrfModuleSerializer


class QuoteDrfSerializer(DrfModuleSerializer):
    """Serializer for quotes."""

    bite = serializers.SerializerMethodField()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'quotes.quote'

    def get_bite(self, instance: 'Quote') -> str:
        """Return the user-facing bite HTML."""
        # Set `bite` to truncated text if it does not exist.
        return instance.bite if instance.bite else truncatechars_html(instance.text, 150)

    class Meta(DrfModuleSerializer.Meta):
        model = Quote
        fields = DrfModuleSerializer.Meta.fields + [
            'bite',
            'html',
            'attributee_html',
            'attributee_string',
            'date_string',
            'cached_images',
            'primary_image',
            'cached_citations',
        ]
