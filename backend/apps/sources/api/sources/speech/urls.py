from rest_framework import routers

from apps.sources.api.sources.speech import views

router = routers.DefaultRouter()
router.register('speeches', views.SpeechViewSet)
