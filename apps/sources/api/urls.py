from django.urls import path
from rest_framework import routers

from apps.sources.api import views

router = routers.DefaultRouter()
router.register(r'sources', views.SourceViewSet)

app_name = 'sources'

urlpatterns = [
    path('', views.SourceListAPIView.as_view()),
]
