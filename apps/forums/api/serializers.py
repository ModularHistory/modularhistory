from rest_framework import serializers

from apps.forums.models import Thread, Post
from core.models.module import DrfModuleSerializer


class ThreadDrfSerializer(serializers.ModelSerializer):
    """Serializer for threads."""

    class Meta:
        model = Thread
        fields = ['pk', 'updated_date']


class PostDrfSerializer(serializers.ModelSerializer):
    """Serializer for posts."""

    class Meta:
        model = Post
        fields = [
            'pk',
            'content',
            'title',
            'date',
            'author',
            'parent_thread',
        ]
        read_only_fields = ['pk']
