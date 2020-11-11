from django.db.models.query import QuerySet
from django.views import generic

from facts.models import Fact


class IndexView(generic.list.ListView):
    """View depicting all topics."""

    model = Fact
    template_name = 'facts/index.html'
    context_object_name = 'facts'

    def get_queryset(self) -> 'QuerySet[Fact]':
        """TODO: add docstring."""
        return Fact.objects.all()


class DetailPartView(generic.detail.DetailView):
    """Partial view for an individual topic."""

    model = Fact
    template_name = 'facts/_detail.html'
    context_object_name = 'fact'


class DetailView(generic.detail.DetailView):
    """View depicting an individual topic."""

    model = Fact
    template_name = 'facts/detail.html'
    context_object_name = 'fact'
