from django.views import generic

from .models import Image


class IndexView(generic.ListView):
    """TODO: add docstring."""

    model = Image
    template_name = 'images/index.html'
    # paginate_by = 10
    context_object_name = 'images'

    def get_queryset(self):
        """Return the last five published questions."""
        return Image.objects.order_by('name')


class DetailView(generic.DetailView):
    """TODO: add docstring."""

    model = Image
    template_name = 'images/detail.html'
    context_object_name = 'image'


class DetailPartView(generic.DetailView):
    """TODO: add docstring."""

    model = Image
    template_name = 'images/_detail.html'
    context_object_name = 'image'
