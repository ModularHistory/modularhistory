"""Serializers for the entities app."""

from rest_framework import serializers

from quotes.models import Quote


class QuoteSerializer(serializers.ModelSerializer):
    """TODO: add docstring."""

    class Meta:
        model = Quote
        fields = [
            'text',
            'bite',
            'pretext',
            'context',
            'date',
            'attributees',
            'images',
        ]
