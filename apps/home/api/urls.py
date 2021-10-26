from django.urls import path

from apps.home.api import views

app_name = 'home'

urlpatterns = [
    path('todayinhistory/', views.TodayInHistoryViewSet.as_view()),
]
