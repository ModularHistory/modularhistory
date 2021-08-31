from django.urls import path

from apps.staticpages.api import views

app_name = 'staticpages'

urlpatterns = [
    path('', views.FlatPageAPIView.as_view()),
    path('<path:url>', views.FlatPageAPIView.as_view()),
]
