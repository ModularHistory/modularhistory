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
