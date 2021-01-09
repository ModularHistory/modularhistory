from django.urls import path
from rest_framework import routers

from apps.topics.api import views

router = routers.DefaultRouter()
router.register(r'topics', views.TopicViewSet)

app_name = 'topics'

urlpatterns = [
    path('', views.TopicListAPIView.as_view()),
]
