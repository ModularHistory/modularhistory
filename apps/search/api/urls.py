from django.urls import include, path

from apps.search.api import views
from apps.search.api.todayinhistory.views import TodayInHistoryViewSet

app_name = 'search'

urlpatterns = [
    path('todayinhistory/', TodayInHistoryViewSet.as_view()),
    path('', views.ElasticSearchResultsAPIView.as_view()),
]
