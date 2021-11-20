from django.urls import path

from apps.moderation.api import views

app_name = 'moderation'

urlpatterns = [
    path('contributions/', views.ContentContributionAPIView.as_view()),
]
