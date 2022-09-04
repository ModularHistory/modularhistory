from django.urls import path

from apps.search.views import word_search

app_name = 'search'

urlpatterns = [
    path('words/<word>', word_search, name='word_search'),
]
