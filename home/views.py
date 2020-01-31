# from django.shortcuts import render
from itertools import chain
from typing import Dict, List, Union

from django.db.models import QuerySet
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from history.models import Model
from home.forms import SearchFilterForm
from images.models import Image
from occurrences.models import Occurrence
from quotes.models import Quote
from sources.models import Source
from datetime import datetime

# from topics.models import Topic, Fact


class HomePageView(TemplateView):
    template_name = 'home/index.html'


def sorter(x: Model):
    weight = x.id
    if hasattr(x, 'date') and x.date:
        weight = 10000 * x.date.year + 100 * x.date.month + x.date.day
    elif hasattr(x, 'year') and x.year:
        weight = 10000 * x.year.common_era
    return weight


# TODO: https://docs.djangoproject.com/en/3.0/topics/db/search/
# TODO: https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/
class SearchResultsView(ListView):
    template_name = 'search_results.html'
    results_count = 0
    paginate_by = 100

    entities: QuerySet

    def get_context_data(self, *args, **kwargs) -> Dict:
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.results_count or 0
        context['query'] = self.request.GET.get('q')

        context['search_filter_form'] = SearchFilterForm()
        return context

    def get_queryset(self) -> Union[QuerySet, List]:
        request = self.request
        query = request.GET.get('q', None)

        if query is not None:
            occurrence_results = Occurrence.objects.search(query)
            # entity_results = Entity.objects.search(query)
            # topic_results = Topic.objects.search(query)
            # fact_results = Fact.objects.search(query)
            quote_results = Quote.objects.search(query)
            # image_results = Image.objects.search(query)
            source_results = Source.objects.search(query).exclude(quotes__in=quote_results)

            # combine querysets
            queryset_chain = chain(
                occurrence_results,
                quote_results,
                # image_results,
                source_results
            )
            qs = sorted(queryset_chain, key=sorter, reverse=False)

            # TODO: From here, we can advance our search even more.
            # This part qs = sorted(queryset_chain, key=lambda instance: instance.pk, reverse=True)
            # shows us we can reorder our responses based on an arbitrary field, or even an instance method.
            # That means we can create a method to calculate "rank" for any given model and any given model
            # instance. This rank, can be based off analytics like link clicks, page views, link social shares,
            # or any other rank parameter we might like. Thus creating a better experience for your searches.

            self.results_count = len(qs)  # since qs is actually a list
            return qs
        return Occurrence.objects.none()  # just an empty queryset as default
