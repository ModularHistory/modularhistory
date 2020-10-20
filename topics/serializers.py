"""Serializers for the entities app."""

from rest_framework import serializers

from topics.models import Topic


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for topics."""

    class Meta:
        model = Topic
        fields = [
            'key',
        ]
