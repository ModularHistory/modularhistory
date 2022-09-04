from django.urls import re_path

from apps.flatpages.api import views
from apps.flatpages.models import URL_PATH_PATTERN

app_name = 'flatpages'

urlpatterns = [
    re_path(
        rf'(?P<path>{URL_PATH_PATTERN})/?$', views.FlatPageAPIView.as_view(), name='flatpage'
    ),
]
