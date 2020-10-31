"""Serializers for the entities app."""

from rest_framework import serializers


class QuoteSerializer(serializers.Serializer):
    """Serializer for quotes."""

    text = serializers.CharField()
    bite = serializers.CharField()
    pretext = serializers.CharField()
    context = serializers.CharField()
    date = serializers.DateTimeField()
