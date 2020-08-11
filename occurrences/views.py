from typing import Dict

from django.views import generic
try:
    from polymorphic import PolymorphicQuerySet
except ImportError:
    from polymorphic.query import PolymorphicQuerySet

from search.forms import SearchFilterForm
from .models import Occurrence


class ListView(generic.list.ListView):
    model = Occurrence
    template_name = 'occurrences/index.html'
    context_object_name = 'occurrences'
    paginate_by = 20

    def get_queryset(self) -> PolymorphicQuerySet:
        """Return the queryset."""
        return Occurrence.objects.all()

    def get_context_data(self, *args, **kwargs) -> Dict:
        context = super().get_context_data(*args, **kwargs)
        context['search_filter_form'] = SearchFilterForm()
        return context


class BaseDetailView(generic.detail.DetailView):
    model = Occurrence
    context_object_name = 'occurrence'

    object: Occurrence

    def get_context_data(self, *args, **kwargs) -> Dict:
        context = super().get_context_data(*args, **kwargs)
        occurrence = self.object
        context = {**context, **occurrence.get_context()}
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
