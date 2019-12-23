from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from people.models import Person


def index(request):
    """lists the users in a table on the screen"""
    people = Person.objects.all().order_by('name')
    context = {
        'people': people
    }
    return render(request, 'people/index.html', context)

def detail(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    return render(request, 'people/detail.html', {'question': question})
