from django.urls import include, path
from rest_framework import routers

from apps.collections.api import views

router = routers.DefaultRouter()
router.register('', views.CollectionViewSet)

app_name = 'collections'

urlpatterns = [
    path('', include(router.urls)),
]
