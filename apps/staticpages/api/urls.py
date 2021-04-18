from django.urls import path
from apps.staticpages.api import views

app_name = 'staticpages'

urlpatterns = [
    path('', views.StaticPageAPIView.as_view()),
    path('<path:url>', views.StaticPageAPIView.as_view()),
]