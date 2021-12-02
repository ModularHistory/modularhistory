from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.forums.api.serializers import PostSerializer, ThreadSerializer
from apps.forums.models import Post, Thread
from core.api.views import ExtendedModelViewSet


class ThreadViewSet(ModelViewSet):
    """API endpoint for viewing and editing threads."""

    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer


class PostViewSet(ModelViewSet):
    """API endpoint for viewing and editing posts."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
