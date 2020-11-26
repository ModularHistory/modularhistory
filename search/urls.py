from django.urls import path

from search.views import SearchResultsView, word_search

app_name = 'search'

urlpatterns = [
    path('words/<word>', word_search, name='word_search'),
    path('', SearchResultsView.as_view(), name='search_results'),
]
