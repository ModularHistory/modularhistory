from django.urls import path

from apps.home import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
]
