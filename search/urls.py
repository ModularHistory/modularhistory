from django.urls import path

from search.views import SearchResultsView, word_search  # type: ignore

urlpatterns = [
    path('words/<word>', word_search, name='word_search'),
    path('', SearchResultsView.as_view(), name='search_results'),
]
