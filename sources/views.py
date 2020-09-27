from typing import Any, Dict

from django.db.models.query import QuerySet
from django.views import generic
from django.views.generic import TemplateView

from quotes.models import Quote
from sources.models import Source


class IndexView(generic.ListView):
    """TODO: add docstring."""

    model = Source
    template_name = 'sources/index.html'
    context_object_name = 'sources'

    def get_queryset(self) -> 'QuerySet[Source]':
        """Return the last five published questions."""
        return Source.objects.all()


class BaseDetailView(generic.DetailView):
    """TODO: add docstring."""

    model = Source
    context_object_name = 'source'
    object: Source

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """TODO: add docstring."""
        context = super().get_context_data(**kwargs)
        containers = [self.object] + list(self.object.contained_sources.all())
        context['quotes'] = Quote.objects.filter(sources__in=containers)
        return context


class DetailView(BaseDetailView):
    """TODO: add docstring."""

    template_name = 'sources/detail.html'


class DetailPartView(BaseDetailView):
    """TODO: add docstring."""

    template_name = 'sources/_detail.html'


class EPubView(TemplateView):
    """TODO: add docstring."""

    template_name = 'sources/_epub_viewer.html'

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """TODO: add docstring."""
        context = super().get_context_data(**kwargs)
        epub_path = self.kwargs['path']
        print(f'>>>>>>> {epub_path}')
        context['path'] = epub_path
        return context
