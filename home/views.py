from typing import Dict, List, Optional

from django.db.models import QuerySet
from django.views.generic import TemplateView  # , RedirectView

from search.forms import SearchForm


class HomePageView(TemplateView):
    """Renders the homepage."""

    template_name = 'home/index.html'

    excluded_content_types: Optional[List[int]] = None
    sort_by_relevance: bool = False
    suppress_unverified: bool = True
    entities: Optional[QuerySet] = None
    topics: Optional[QuerySet] = None
    places: Optional[QuerySet] = None
    db: str = 'default'

    def get_context_data(self, **kwargs) -> Dict:
        """Return the context data used in rendering the homepage."""
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        context['query'] = query

        search_form = SearchForm(
            request=self.request,
            query=query,
            suppress_unverified=self.suppress_unverified,
            order_by_relevance=self.sort_by_relevance,
            excluded_content_types=self.excluded_content_types,
            entities=self.entities,
            topics=self.topics,
            collapse_refinements=True,
        )
        context['search_form'] = search_form
        return context
