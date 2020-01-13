from django.views import generic

from .models import Source


class IndexView(generic.ListView):
    model = Source
    template_name = 'sources/index.html'
    context_object_name = 'sources'

    def get_queryset(self):
        """Return the last five published questions."""
        return Source.objects.all()


class DetailView(generic.DetailView):
    model = Source
    template_name = 'sources/detail.html'
    context_object_name = 'source'


class DetailPartView(generic.DetailView):
    model = Source
    template_name = 'sources/_detail.html'
    context_object_name = 'source'
