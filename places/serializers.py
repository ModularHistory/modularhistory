"""Serializers for the entities app."""


from rest_framework import serializers

from places.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    """Serializer for places."""

    string = serializers.CharField(source='string')

    class Meta:
        model = Place
        fields = [
            'name',
            'location',
            'string',
        ]
