from django.urls import path
from rest_framework import routers

from apps.stories.api import views

router = routers.DefaultRouter()
<<<<<<< HEAD
router.register(r'stories', views.StoryViewSet)
=======
router.register(r'stories', views.PostulationViewSet)
>>>>>>> MH-162: add stories app

app_name = 'stories'

urlpatterns = [
<<<<<<< HEAD
    path('', views.StoryListAPIView.as_view()),
=======
    path('', views.PostulationListAPIView.as_view()),
>>>>>>> MH-162: add stories app
]
