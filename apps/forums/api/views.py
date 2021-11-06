from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.forums.api.serializers import ThreadDrfSerializer, PostDrfSerializer
from apps.forums.models import Thread, Post
from core.api.views import ExtendedModelViewSet
from rest_framework.viewsets import ModelViewSet


class ThreadViewSet(ModelViewSet):
    """API endpoint for viewing and editing threads."""

    queryset = Thread.objects.all()
    serializer_class = ThreadDrfSerializer


class PostViewSet(ModelViewSet):
    """API endpoint for viewing and editing posts."""

    queryset = Post.objects.all()
    serializer_class = PostDrfSerializer
