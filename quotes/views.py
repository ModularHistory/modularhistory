"""Views for the quotes app."""

from typing import Dict

from django.views import generic

from modularhistory.constants import IMAGE_CT_ID, OCCURRENCE_CT_ID, SOURCE_CT_ID
from quotes.models import Quote
from search.forms import SearchForm


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
            excluded_content_types=[OCCURRENCE_CT_ID, IMAGE_CT_ID, SOURCE_CT_ID],
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
