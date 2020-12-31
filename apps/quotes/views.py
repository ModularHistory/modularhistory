"""Views for the quotes app."""

from typing import Any, Dict, Optional

from django.views import generic
from meta.views import Meta

from apps.quotes.models import Quote
from apps.search.forms import SearchForm
from modularhistory.constants.content_types import ModelNameSet


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
            excluded_content_types=[
                ModelNameSet.occurrence,
                ModelNameSet.image,
                ModelNameSet.source,
            ],
        )
        context['meta'] = Meta(
            title='Quotes',
            description=(
                'Quotes by historical and contemporary entities, '
                'filterable by attributee, topic, and more.'
            ),
        )
        return context


class BaseDetailView(generic.detail.DetailView):
    """Abstract view showing details of a specific quote."""

    model = Quote
    context_object_name = 'quote'
    query_pk_and_slug = True

    object: Quote

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context data used to render the view."""
        context = super().get_context_data(*args, **kwargs)
        context['quote'] = self.object.serialize()
        return context


class DetailView(BaseDetailView):
    """View showing details of a specific quote."""

    template_name = 'quotes/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quote: Quote = self.object
        image: Optional[Dict[str, Any]] = quote.primary_image
        img_src = image['src_url'] if image else None
        context['meta'] = Meta(
            title=f'{quote.attributee_string}, {quote.date_string}',
            description=f'{quote.attributee_string}, {quote.date_string}: {quote.bite.text}',
            keywords=quote.tag_keys,
            image=img_src,
        )
        return context


class DetailPartView(BaseDetailView):
    """Partial view showing details of a specific quote."""

    template_name = 'quotes/_detail.html'
