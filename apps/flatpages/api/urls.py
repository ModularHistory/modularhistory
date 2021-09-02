from django.urls import path

from apps.flatpages.api import views

app_name = 'flatpages'

urlpatterns = [
    path('', views.FlatPageAPIView.as_view()),
    path('<path:url>', views.FlatPageAPIView.as_view(), name='flatpage'),
]
