from typing import Any, Dict, Optional

from django.views import generic
from meta.views import Meta

from apps.occurrences.models import Occurrence
from apps.search.forms import SearchForm
from modularhistory.constants.content_types import ContentTypes


class ListView(generic.list.ListView):
    """View that listing all occurrences."""

    model = Occurrence
    template_name = 'occurrences/index.html'
    context_object_name = 'occurrences'
    paginate_by = 15

    def get_queryset(self):
        """Return the queryset."""
        return [occurrence.serialize() for occurrence in Occurrence.objects.iterator()]

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context dictionary used to render the view."""
        context = super().get_context_data(*args, **kwargs)
        context['search_form'] = SearchForm(
            request=self.request,
            excluded_content_types=[
                ContentTypes.quote,
                ContentTypes.image,
                ContentTypes.source,
            ],
        )
        context['meta'] = Meta(
            title='Occurrences',
            description=(
                'Historical occurrences, filterable by topic, involved entities, and more.'
            ),
        )
        return context


class BaseDetailView(generic.detail.DetailView):
    """Abstract view that displays details of a specific occurrence."""

    model = Occurrence
    context_object_name = 'occurrence'
    query_pk_and_slug = True

    object: Occurrence

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context dictionary used to render the view."""
        context = super().get_context_data(*args, **kwargs)
        occurrence = self.object
        context_data = {**context, **occurrence.get_context()}  # TODO
        context_data['occurrence'] = occurrence.serialize()
        return context_data


class DetailView(BaseDetailView):
    """View that displays details of a specific occurrence."""

    template_name = 'occurrences/detail.html'

    def get_context_data(self, **kwargs):
        """Return the context dictionary used to render the view."""
        context = super().get_context_data(**kwargs)
        occurrence = self.object
        image: Optional[Dict[str, Any]] = occurrence.primary_image
        img_src = image['src_url'] if image else None
        summary = occurrence.summary
        context['meta'] = Meta(
            title=summary,
            description=f'Information regarding the {summary.text}',
            keywords=occurrence.tag_keys,
            image=img_src,
        )
        return context


class DetailPartialView(BaseDetailView):
    """Partial view that displays details of a specific occurrence."""

    template_name = 'occurrences/_detail.html'
