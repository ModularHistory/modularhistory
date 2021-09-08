from django.urls import include, path
from rest_framework import routers

from apps.sources.api import views

router = routers.DefaultRouter()
router.register('', views.SourceViewSet)

app_name = 'sources'

urlpatterns = [
    path('', include(router.urls)),
]
