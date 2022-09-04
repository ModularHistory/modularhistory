from django.urls import re_path

from apps.flatpages.models import URL_PATH_PATTERN
from apps.redirects.api import views

app_name = 'redirects'

urlpatterns = [
    re_path(rf'(?P<old_path>{URL_PATH_PATTERN})/?$', views.RedirectAPIView.as_view()),
    re_path('', views.RedirectListAPIView.as_view()),
]
