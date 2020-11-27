from django.db.models.query import QuerySet
from django.views import generic

from postulations.models import Postulation


class IndexView(generic.list.ListView):
    """View depicting all topics."""

    model = Postulation
    template_name = 'postulations/index.html'
    context_object_name = 'postulations'

    def get_queryset(self) -> 'QuerySet[Postulation]':
        """TODO: add docstring."""
        return Postulation.objects.all()


class DetailPartView(generic.detail.DetailView):
    """Partial view for an individual topic."""

    model = Postulation
    template_name = 'postulations/_detail.html'
    context_object_name = 'fact'


class DetailView(generic.detail.DetailView):
    """View depicting an individual topic."""

    model = Postulation
    template_name = 'postulations/detail.html'
    context_object_name = 'fact'
