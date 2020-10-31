"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers


class OccurrenceSerializer(serializers.Serializer):
    """Serializer for occurrences."""

    date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    summary = serializers.CharField()
    description = serializers.CharField()
