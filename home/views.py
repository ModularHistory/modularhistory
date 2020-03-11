# from django.shortcuts import render

from django.views.generic import TemplateView  # , RedirectView


class HomePageView(TemplateView):
    template_name = 'home/index.html'


# class HomePageView(TemplateView):
#     template_name = 'home/index.html'
#
#
# class HomePageView(TemplateView):
#     template_name = 'home/index.html'
