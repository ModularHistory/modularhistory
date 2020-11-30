from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from django.db.models.query import QuerySet
from django.views import generic

from apps.topics.models import Topic


class TagSearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self) -> 'QuerySet[Topic]':
        """Return the filtered queryset."""
        queryset = Topic.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(key__icontains=term) | Q(aliases__icontains=term)
            )
        return queryset


class IndexView(generic.list.ListView):
    """View depicting all topics."""

    model = Topic
    template_name = 'topics/index.html'
    context_object_name = 'topics'

    def get_queryset(self) -> 'QuerySet[Topic]':
        """TODO: add docstring."""
        return Topic.objects.all()


class DetailPartView(generic.detail.DetailView):
    """Partial view for an individual topic."""

    model = Topic
    template_name = 'topics/_detail.html'
    context_object_name = 'topic'


class DetailView(generic.detail.DetailView):
    """View depicting an individual topic."""

    model = Topic
    template_name = 'topics/detail.html'
    context_object_name = 'topic'
