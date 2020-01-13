from django.views import generic

from .models import Topic


class IndexView(generic.list.ListView):
    model = Topic
    template_name = 'topics/index.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.all()


class DetailPartView(generic.detail.DetailView):
    model = Topic
    template_name = 'topics/_detail.html'
    context_object_name = 'topic'


class DetailView(generic.detail.DetailView):
    model = Topic
    template_name = 'topics/detail.html'
    context_object_name = 'topic'
