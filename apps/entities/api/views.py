from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from modularhistory.views import AsyncAPIViewMixin
from apps.entities.models import Category, Entity  # , Person, Organization
from apps.entities.serializers import EntitySerializer


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class EntityListAPIView(AsyncAPIViewMixin, ListAPIView):
    """API view for listing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer
