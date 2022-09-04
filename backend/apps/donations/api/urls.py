from django.urls import path
from rest_framework import routers

from apps.donations.api import views

router = routers.DefaultRouter()

app_name = 'donations'

urlpatterns = [
    path('token/', views.get_token),
    path('process/', views.process),
]
