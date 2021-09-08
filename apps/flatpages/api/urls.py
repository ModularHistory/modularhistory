from django.urls import path

from apps.flatpages.api import views

app_name = 'flatpages'

urlpatterns = [
    path('<path:path>', views.FlatPageAPIView.as_view(), name='flatpage'),
]
