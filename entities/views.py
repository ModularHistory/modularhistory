from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.views import generic

from entities.models import Entity  # , Person, Organization


class EntitySearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """TODO: add docstring."""
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Entity.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term) |
                Q(aliases__icontains=term)
            )
        return queryset


class IndexView(generic.ListView):
    """TODO: add docstring."""

    model = Entity
    template_name = 'entities/index.html'
    # paginate_by = 10
    context_object_name = 'entities'

    def get_queryset(self):
        """Return the last five published questions."""
        return Entity.objects.exclude(type='entities.deity').order_by('birth_date')


class BaseDetailView(generic.detail.DetailView):
    """TODO: add docstring."""

    model = Entity
    context_object_name = 'entity'


class DetailView(BaseDetailView):
    template_name = 'entities/detail.html'


class DetailPartView(BaseDetailView):
    template_name = 'entities/_detail.html'
