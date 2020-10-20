"""Serializers for the entities app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/

from rest_framework import serializers

from sources.models import Source


class SourceSerializer(serializers.ModelSerializer):
    """Serializer for sources."""

    html = serializers.CharField(source='html')

    class Meta:
        model = Source
        fields = [
            'html',
        ]
