from django.urls import path

from apps.cms.api import views

app_name = 'cms'

urlpatterns = [
    path('branches/create/', views.BranchCreationView.as_view()),
    path('issues/', views.IssueListView.as_view()),
    path('issues/<int:number>/', views.IssueView.as_view()),
    path('issues/create/', views.IssueCreationView.as_view()),
    path('pull_requests/', views.PullRequestListView.as_view()),
    path('pull_requests/<int:number>/', views.PullRequestView.as_view()),
    path('pull_requests/create/', views.PullRequestCreationView.as_view()),
]
