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


class EntitySearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self):
        """Return the filtered queryset."""
        queryset = Entity.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term)
                | Q(unabbreviated_name__icontains=term)
                | Q(aliases__icontains=term)
            )
        return queryset


class EntityCategorySearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self):
        """Return the filtered queryset."""
        queryset = Category.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term) | Q(aliases__icontains=term)
            )
        return queryset
