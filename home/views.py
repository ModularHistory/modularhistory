# from django.shortcuts import render

from django.views.generic import TemplateView, RedirectView

# from topics.models import Topic, Fact


class HomePageView(RedirectView, TemplateView):
    permanent = False
    pattern_name = 'search'

    # template_name = 'home/index.html'
