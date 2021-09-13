from django.urls import re_path

from apps.redirects.api import views

app_name = 'redirects'

urlpatterns = [
    re_path('', views.RedirectListAPIView.as_view()),
]
