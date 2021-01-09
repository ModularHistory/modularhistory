from django.urls import path
from rest_framework import routers

from apps.postulations.api import views

router = routers.DefaultRouter()
router.register(r'postulations', views.PostulationViewSet)

app_name = 'postulations'

urlpatterns = [
    path('', views.PostulationListAPIView.as_view()),
]
