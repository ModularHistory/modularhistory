from django.urls import path
from rest_framework import routers

from apps.stories.api import views

router = routers.DefaultRouter()
router.register(r'stories', views.StoryViewSet)

app_name = 'stories'

urlpatterns = [
    path('', views.StoryListAPIView.as_view()),
]
