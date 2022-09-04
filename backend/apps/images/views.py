from django.views import generic

from apps.images.models import Image


class IndexView(generic.ListView):
    """List view of all images."""

    model = Image
    template_name = 'images/index.html'
    paginate_by = 20
    context_object_name = 'images'

    def get_queryset(self):
        """Return the last five published questions."""
        return Image.objects.order_by('name')


class DetailView(generic.DetailView):
    """View depicting details of a specific image."""

    model = Image
    template_name = 'images/detail.html'
    context_object_name = 'image'


class DetailPartView(generic.DetailView):
    """Partial view depicting details of a specific image."""

    model = Image
    template_name = 'images/_detail.html'
    context_object_name = 'image'
