from django.views import generic
from typing import Dict
from .models import Source
from quotes.models import Quote  #, QuoteSourceReference


class IndexView(generic.ListView):
    model = Source
    template_name = 'sources/index.html'
    context_object_name = 'sources'

    def get_queryset(self):
        """Return the last five published questions."""
        return Source.objects.all()


class BaseDetailView(generic.DetailView):
    model = Source
    context_object_name = 'source'
    object: Source

    def get_context_data(self, **kwargs) -> Dict:
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
