from rest_framework import routers

from apps.sources.api.sources.interview import views

router = routers.DefaultRouter()
router.register('interviews', views.InterviewViewSet)
