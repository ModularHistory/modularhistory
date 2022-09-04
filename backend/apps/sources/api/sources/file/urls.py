from rest_framework import routers

from apps.sources.api.sources.file import views

router = routers.DefaultRouter()
router.register('files', views.SourceFileViewSet)
