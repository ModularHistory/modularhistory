from django.urls import path

from apps.search.api import views

app_name = 'search'

urlpatterns = [
    path('', views.ElasticSearchResultsAPIView.as_view()),
]
