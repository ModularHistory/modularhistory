from django.views import generic

from apps.places.models import Place


class IndexView(generic.list.ListView):
    """List view for places."""

    model = Place
    template_name = 'places/index.html'
    context_object_name = 'places'

    def get_queryset(self):
        """Return the last five published questions."""
        return Place.objects.order_by('name')


class DetailView(generic.detail.DetailView):
    """Detail view for places."""

    model = Place
    template_name = 'places/detail.html'
    context_object_name = 'place'


class DetailPartView(generic.detail.DetailView):
    """Partial detail view for places."""

    model = Place
    template_name = 'places/_detail.html'
    context_object_name = 'place'
