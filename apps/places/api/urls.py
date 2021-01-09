from django.urls import path
from rest_framework import routers

from apps.places.api import views

router = routers.DefaultRouter()
router.register(r'places', views.PlaceViewSet)

app_name = 'places'

urlpatterns = [
    path('', views.PlaceListAPIView.as_view()),
]
