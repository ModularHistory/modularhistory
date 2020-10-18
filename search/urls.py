from django.urls import path

from search.views import SearchResultsView  # type: ignore

urlpatterns = [
    path('', SearchResultsView.as_view(), name='search_results'),
]
