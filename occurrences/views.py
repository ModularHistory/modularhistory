from typing import Dict

from django.views import generic
from polymorphic.query import PolymorphicQuerySet

from quotes.models import Quote
from search.forms import SearchFilterForm
from .models import Occurrence


class ListView(generic.list.ListView):
    model = Occurrence
    template_name = 'occurrences/index.html'
    context_object_name = 'occurrences'
    paginate_by = 20

    def get_queryset(self) -> PolymorphicQuerySet:
        """Return the queryset."""
        return Occurrence.objects.exclude(related_topics__key='Mormonism')  # TODO

    def get_context_data(self, *args, **kwargs) -> Dict:
        context = super().get_context_data(*args, **kwargs)
        context['search_filter_form'] = SearchFilterForm()
        return context


def quote_sorter_key(quote: Quote):
    x = 0
    if quote.date:
        date = quote.date
        x += 1000000000000*date.year + 1000000000*date.month + 1000000*date.day
    if quote.citation:
        citation = quote.citation
        number = ord(str(citation)[0].lower()) - 96
        x += number*1000
        if citation.page_number:
            x += citation.page_number
    return x


class BaseDetailView(generic.detail.DetailView):
    model = Occurrence
    context_object_name = 'occurrence'

    object: Occurrence

    def get_context_data(self, *args, **kwargs) -> Dict:
        context = super().get_context_data(*args, **kwargs)

        context['quotes'] = sorted(self.object.related_quotes.all(), key=quote_sorter_key)

        # 'unpositioned_images' is a little misleading;
        # these are positioned by their `position` attribute rather than manually positioned.
        context['unpositioned_images'] = self.object.occurrence_images.exclude(position=0)

        return context


class DetailView(BaseDetailView):
    template_name = 'occurrences/detail.html'


class DetailPartialView(BaseDetailView):
    template_name = 'occurrences/_detail.html'


# def add(request):
#     """add an occurrence"""
#     num_divisions = request.GET.get('numDivisions') if 'numDivisions' in request.GET else None
#     form = CreateForm(request, num_divisions=(num_divisions if num_divisions else 3))
#     if request.method == 'POST': # just submitted the form
#         form = CreateForm(request, num_divisions=(num_divisions if num_divisions else 3))
#         if form.is_valid():
#             event = form.save()
#             return HttpResponseRedirect('/events/manage/')
#     context = {
#         'form': form,
#     }
#     return request.dmp.render('event.create.html', context)
