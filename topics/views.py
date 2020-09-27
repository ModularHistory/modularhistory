from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from django.db.models.query import QuerySet
# from django.http import HttpRequest, JsonResponse
from django.views import generic

from topics.models import Topic


class TagSearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    # def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
    #     """TODO: add docstring."""
    #     return super().get(request, *args, **kwargs)

    def get_queryset(self) -> 'QuerySet[Topic]':
        """TODO: add docstring."""
        queryset = Topic.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(key__icontains=term) |
                Q(aliases__icontains=term)
            )
        return queryset


class IndexView(generic.list.ListView):
    """TODO: add docstring."""

    model = Topic
    template_name = 'topics/index.html'
    context_object_name = 'topics'

    def get_queryset(self) -> 'QuerySet[Topic]':
        """TODO: add docstring."""
        return Topic.objects.all()


class DetailPartView(generic.detail.DetailView):
    """TODO: add docstring."""

    model = Topic
    template_name = 'topics/_detail.html'
    context_object_name = 'topic'


class DetailView(generic.detail.DetailView):
    """TODO: add docstring."""

    model = Topic
    template_name = 'topics/detail.html'
    context_object_name = 'topic'
