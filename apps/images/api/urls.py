from django.urls import path
from rest_framework import routers

from apps.images.api import views

router = routers.DefaultRouter()
router.register(r'images', views.ImageViewSet)

app_name = 'images'

urlpatterns = [
    path('', views.ImageListAPIView.as_view()),
]
