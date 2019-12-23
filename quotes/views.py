from django.views import generic

from .models import Quote


class IndexView(generic.list.ListView):
    model = Quote
    template_name = 'quotes/index.html'
    context_object_name = 'quotes'

    def get_queryset(self):
        return Quote.objects.all()


class DetailView(generic.detail.DetailView):
    model = Quote
    template_name = 'quotes/detail.html'
