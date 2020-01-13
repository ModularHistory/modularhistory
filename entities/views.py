from django.views import generic

from .models import Entity  # , Person, Organization


class IndexView(generic.ListView):
    model = Entity
    template_name = 'entities/index.html'
    # paginate_by = 10
    context_object_name = 'entities'

    def get_queryset(self):
        """Return the last five published questions."""
        return Entity.objects.order_by('name')


class BaseDetailView(generic.detail.DetailView):
    model = Entity
    context_object_name = 'entity'


class DetailView(BaseDetailView):
    template_name = 'entities/detail.html'


class DetailPartView(BaseDetailView):
    template_name = 'entities/_detail.html'
