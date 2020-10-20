"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers

from occurrences.models import Occurrence


class OccurrenceSerializer(serializers.ModelSerializer):
    """Serializer for occurrences."""

    class Meta:
        model = Occurrence
        fields = [
            'date',
            'end_date',
            'summary',
            'description',
            'postscript',
            'locations',
            'images',
            'involved_entities',
            'chains',
        ]
