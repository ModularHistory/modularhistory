from django.urls import include, path
from rest_framework import routers

from apps.images.api import views

router = routers.DefaultRouter()
router.register('videos', views.VideoViewSet)
router.register('', views.ImageViewSet)

app_name = 'images'

urlpatterns = [
    path('', include(router.urls)),
]
