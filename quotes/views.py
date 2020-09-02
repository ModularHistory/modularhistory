from typing import Dict

from django.views import generic

from search.models import Search
from search.forms import SearchForm
from .models import Quote


class ListView(generic.list.ListView):
    """TODO: add docstring."""

    model = Quote
    template_name = 'quotes/index.html'
    context_object_name = 'quotes'
    paginate_by = 20

    def get_queryset(self):
        """TODO: add docstring."""
        return Quote.objects.filter(verified=True)

    def get_context_data(self, *args, **kwargs) -> Dict:
        """TODO: add docstring."""
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = SearchForm(
            request=self.request,
            excluded_content_types=[Search.get_occurrence_ct(), Search.get_image_ct(), Search.get_source_ct()]
        )
        return context


class BaseDetailView(generic.detail.DetailView):
    """TODO: add docstring."""

    model = Quote
    context_object_name = 'quote'


class DetailView(BaseDetailView):
    """TODO: add docstring."""

    template_name = 'quotes/detail.html'


class DetailPartView(BaseDetailView):
    """TODO: add docstring."""

    template_name = 'quotes/_detail.html'
