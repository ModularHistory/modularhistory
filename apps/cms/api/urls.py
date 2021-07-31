from django.urls import path

from apps.cms.api import views

app_name = 'cms'

urlpatterns = [
    path('branches/create/', views.BranchCreationView.as_view()),
    path('pull_requests/<int:number>/', views.PullRequestView.as_view()),
    path('pull_requests/create/', views.PullRequestCreationView.as_view()),
]
