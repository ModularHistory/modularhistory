from django.urls import include, path
from rest_framework import routers

from apps.places.api import views

router = routers.DefaultRouter()
router.register('', views.PlaceViewSet)

app_name = 'places'

urlpatterns = [
    path('', include(router.urls)),
]
