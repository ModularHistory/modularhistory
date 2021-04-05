from django.urls import path
from rest_framework import routers

from apps.stories.api import views

router = routers.DefaultRouter()
router.register(r'stories', views.PostulationViewSet)

app_name = 'stories'

urlpatterns = [
    path('', views.PostulationListAPIView.as_view()),
]
