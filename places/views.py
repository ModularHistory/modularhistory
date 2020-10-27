from django.views import generic

from places.models import Place


class IndexView(generic.list.ListView):
    """TODO: add docstring."""

    model = Place
    template_name = 'places/index.html'
    context_object_name = 'places'

    def get_queryset(self):
        """Return the last five published questions."""
        return Place.objects.order_by('name')


class DetailView(generic.detail.DetailView):
    """TODO: add docstring."""

    model = Place
    template_name = 'places/detail.html'
    context_object_name = 'place'


class DetailPartView(generic.detail.DetailView):
    """TODO: add docstring."""

    model = Place
    template_name = 'places/_detail.html'
    context_object_name = 'place'


# def add(request):
#     """add an occurrence."""
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
