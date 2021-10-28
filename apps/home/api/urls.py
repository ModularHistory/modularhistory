from django.urls import path

from apps.home.api import views

app_name = 'home'

urlpatterns = [
    path('feature/', views.FeatureAPIView.as_view()),
]
