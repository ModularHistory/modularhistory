from django.views import generic

from .models import Quote


class IndexView(generic.list.ListView):
    model = Quote
    template_name = 'quotes/index.html'
    context_object_name = 'quotes'
    paginate_by = 20

    def get_queryset(self):
        print('Hi')
        return Quote.objects.all()


class BaseDetailView(generic.detail.DetailView):
    model = Quote
    context_object_name = 'quote'


class DetailView(BaseDetailView):
    template_name = 'quotes/detail.html'


class DetailPartView(BaseDetailView):
    template_name = 'quotes/_detail.html'
