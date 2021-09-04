from django.urls import include, path
from rest_framework import routers

from apps.images.api import views

router = routers.DefaultRouter()
router.register(r'', views.ImageViewSet)

app_name = 'images'

urlpatterns = [
    path('', include(router.urls)),
]
