# from django.shortcuts import render

from django.views.generic import TemplateView, RedirectView

# from topics.models import Topic, Fact


class HomePageView(TemplateView):
    template_name = 'home/index.html'
