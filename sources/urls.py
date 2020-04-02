from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/part', views.DetailPartView.as_view(), name='detail_part'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('pdf', TemplateView.as_view(template_name='sources/_pdf_viewer.html')),
    path('epub/<path:path>', views.EPubView.as_view()),
]
