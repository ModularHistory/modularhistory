# from django.http import HttpRequest, JsonResponse

from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from django.db.models.query import QuerySet
# from django.http import HttpRequest, JsonResponse
from django.views import generic
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from entities.models import Entity, Category  # , Person, Organization
from entities.serializers import EntitySerializer


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class EntityListAPIView(ListAPIView):
    """API view for listing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer


class AttributeeSearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self) -> 'QuerySet[Entity]':
        """Returns the filtered queryset."""
        queryset = Entity.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term) |
                Q(unabbreviated_name__icontains=term) |
                Q(aliases__icontains=term)
            )
        return queryset


class EntitySearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self):
        """Returns the filtered queryset."""
        queryset = Entity.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term) |
                Q(aliases__icontains=term)
            )
        return queryset


class EntityCategorySearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self):
        """Returns the filtered queryset."""
        queryset = Category.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term) |
                Q(aliases__icontains=term)
            )
        return queryset


class IndexView(generic.ListView):
    """View depicting all entities."""

    model = Entity
    template_name = 'entities/index.html'
    # paginate_by = 10
    context_object_name = 'entities'

    def get_queryset(self):
        """Return the last five published questions."""
        return Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore


class BaseDetailView(generic.detail.DetailView):
    """Base class for entity detail views."""

    model = Entity
    context_object_name = 'entity'


class DetailView(BaseDetailView):
    """View depicting details of a specific entity."""

    template_name = 'entities/detail.html'


class DetailPartView(BaseDetailView):
    """Partial view depicting details of a specific entity."""

    template_name = 'entities/_detail.html'
