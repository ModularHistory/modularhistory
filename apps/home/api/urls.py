from django.urls import path

from apps.home.api import views

app_name = 'home'

urlpatterns = [
    path('today_in_history/', views.TodayInHistoryView.as_view()),
]
