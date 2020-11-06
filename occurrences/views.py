from typing import Dict

from django.views import generic

from modularhistory.constants.misc import IMAGE_CT_ID, QUOTE_CT_ID, SOURCE_CT_ID
from occurrences.models import Occurrence
from search.forms import SearchForm


class ListView(generic.list.ListView):
    """View that listing all occurrences."""

    model = Occurrence
    template_name = 'occurrences/index.html'
    context_object_name = 'occurrences'
    paginate_by = 5

    def get_queryset(self):
        """Return the queryset."""
        return [
            occurrence.serialize()
            for occurrence in Occurrence.objects.filter(verified=True).iterator()
        ]

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context data used to render the list view."""
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = SearchForm(
            request=self.request,
            excluded_content_types=[QUOTE_CT_ID, IMAGE_CT_ID, SOURCE_CT_ID],
        )
        return context


class BaseDetailView(generic.detail.DetailView):
    """Abstract view that displays details of a specific occurrence."""

    model = Occurrence
    context_object_name = 'occurrence'

    object: Occurrence

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context data used to render the view."""
        context = super().get_context_data(*args, **kwargs)
        occurrence = self.object
        context_data = {**context, **occurrence.get_context()}  # TODO
        context_data['occurrence'] = occurrence.serialize()
        return context_data


class DetailView(BaseDetailView):
    """View that displays details of a specific occurrence."""

    template_name = 'occurrences/detail.html'


class DetailPartialView(BaseDetailView):
    """Partial view that displays details of a specific occurrence."""

    template_name = 'occurrences/_detail.html'
