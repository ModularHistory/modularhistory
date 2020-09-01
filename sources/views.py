from typing import Any, Dict

from django.db.models.query import QuerySet
from django.views import generic
from django.views.generic import TemplateView

from quotes.models import Quote
from .models import Source


class IndexView(generic.ListView):
    model = Source
    template_name = 'sources/index.html'
    context_object_name = 'sources'

    def get_queryset(self) -> 'QuerySet[Source]':
        """Return the last five published questions."""
        return Source.objects.all()


class BaseDetailView(generic.DetailView):
    model = Source
    context_object_name = 'source'
    object: Source

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        containers = [self.object] + [
            contained_source for contained_source in self.object.contained_sources.all()
        ]
        context['quotes'] = Quote.objects.filter(sources__in=containers)
        return context


class DetailView(BaseDetailView):
    template_name = 'sources/detail.html'


class DetailPartView(BaseDetailView):
    template_name = 'sources/_detail.html'


class EPubView(TemplateView):
    template_name = 'sources/_epub_viewer.html'

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        epub_path = self.kwargs['path']
        print(f'>>>>>>> {epub_path}')
        context['path'] = epub_path
        return context
