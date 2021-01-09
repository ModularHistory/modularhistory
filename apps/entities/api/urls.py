from django.urls import path
from rest_framework import routers

from apps.entities.api import views

router = routers.DefaultRouter()
router.register(r'entities', views.EntityViewSet)

app_name = 'entities'

urlpatterns = [
    path('', views.EntityListAPIView.as_view()),
]
