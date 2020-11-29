"""Views for the quotes app."""

from typing import Dict

from django.views import generic

from modularhistory.constants.misc import IMAGE_CT_ID, OCCURRENCE_CT_ID, SOURCE_CT_ID
from quotes.models import Quote
from search.forms import SearchForm


class ListView(generic.list.ListView):
    """View that lists all quotes.."""

    model = Quote
    template_name = 'quotes/index.html'
    context_object_name = 'quotes'
    paginate_by = 10

    def get_queryset(self):
        """Return the queryset."""
        return [
            quote.serialize()
            for quote in Quote.objects.filter(verified=True).iterator()
        ]

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context data used to render the view."""
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = SearchForm(
            request=self.request,
            excluded_content_types=[OCCURRENCE_CT_ID, IMAGE_CT_ID, SOURCE_CT_ID],
        )
        return context


class BaseDetailView(generic.detail.DetailView):
    """Abstract view showing details of a specific quote."""

    model = Quote
    context_object_name = 'quote'
    query_pk_and_slug = True


class DetailView(BaseDetailView):
    """View showing details of a specific quote."""

    template_name = 'quotes/detail.html'


class DetailPartView(BaseDetailView):
    """Partial view showing details of a specific quote."""

    template_name = 'quotes/_detail.html'
