from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic
from .models import Person


class IndexView(generic.ListView):
    model = Person
    template_name = 'people/index.html'
    context_object_name = 'people'

    def get_queryset(self):
        """Return the last five published questions."""
        return Person.objects.order_by('name')


class DetailView(generic.DetailView):
    model = Person
    template_name = 'people/detail.html'
