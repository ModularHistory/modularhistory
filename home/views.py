# from django.shortcuts import render
from typing import Dict, List, Optional, Tuple

from django.db.models import QuerySet
from django.views.generic import TemplateView  # , RedirectView

from search.forms import SearchFilterForm


class HomePageView(TemplateView):
    template_name = 'home/index.html'

    excluded_content_types: Optional[List[Tuple[int, str]]] = None
    sort_by_relevance: bool = False
    suppress_unverified: bool = True
    entities: Optional[QuerySet] = None
    topics: Optional[QuerySet] = None
    places: Optional[QuerySet] = None
    db: str = 'default'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        context['query'] = query

        # Initial data
        # data = {
        #     'excluded_content_types': None,
        #     'entities': None,
        #     'topics': None,
        # }

        search_form = SearchFilterForm(
            request=self.request,
            query=query,
            suppress_unverified=self.suppress_unverified,
            order_by_relevance=self.sort_by_relevance,
            excluded_content_types=self.excluded_content_types,
            entities=self.entities,
            topics=self.topics,
            # places=self.places
            # initial=data
        )
        context['search_form'] = search_form
        return context


# class HomePageView(TemplateView):
#     template_name = 'home/index.html'
#
#
# class HomePageView(TemplateView):
#     template_name = 'home/index.html'
