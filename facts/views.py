from django.db.models.query import QuerySet
from django.views import generic

from facts.models import Postulation


class IndexView(generic.list.ListView):
    """View depicting all topics."""

    model = Postulation
    template_name = 'facts/index.html'
    context_object_name = 'facts'

    def get_queryset(self) -> 'QuerySet[Postulation]':
        """TODO: add docstring."""
        return Postulation.objects.all()


class DetailPartView(generic.detail.DetailView):
    """Partial view for an individual topic."""

    model = Postulation
    template_name = 'facts/_detail.html'
    context_object_name = 'fact'


class DetailView(generic.detail.DetailView):
    """View depicting an individual topic."""

    model = Postulation
    template_name = 'facts/detail.html'
    context_object_name = 'fact'
