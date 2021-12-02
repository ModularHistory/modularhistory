from rest_framework import serializers

from apps.forums.models import Post, Thread
from core.models.serializers import DrfModuleSerializer


class ThreadSerializer(serializers.ModelSerializer):
    """Serializer for threads."""

    class Meta:
        model = Thread
        fields = ['pk', 'updated_date', 'initial_post']


class PostSerializer(serializers.ModelSerializer):
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
