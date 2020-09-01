from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from django.views import generic
from django.http import HttpRequest, JsonResponse
from django.db.models.query import QuerySet
from topics.models import Topic


class TagSearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> 'QuerySet[Topic]':
        queryset = Topic.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(key__icontains=term) |
                Q(aliases__icontains=term)
            )
        return queryset


class IndexView(generic.list.ListView):
    model = Topic
    template_name = 'topics/index.html'
    context_object_name = 'topics'

    def get_queryset(self) -> 'QuerySet[Topic]':
        return Topic.objects.all()


class DetailPartView(generic.detail.DetailView):
    model = Topic
    template_name = 'topics/_detail.html'
    context_object_name = 'topic'


class DetailView(generic.detail.DetailView):
    model = Topic
    template_name = 'topics/detail.html'
    context_object_name = 'topic'
