from django.urls import path

from apps.propositions.api import views

app_name = 'propositions'

urlpatterns = [
    path('', views.PropositionListAPIView.as_view()),
    path('<slug:slug>/', views.PropositionAPIView.as_view()),
    path('<slug:slug>/moderation/', views.PropositionModerationAPIView.as_view()),
]
