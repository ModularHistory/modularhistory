from django.urls import include, path
from rest_framework import routers

from apps.topics.api import views

router = routers.DefaultRouter()
router.register('', views.TopicViewSet)

app_name = 'topics'

urlpatterns = [
    path('', include(router.urls)),
]
