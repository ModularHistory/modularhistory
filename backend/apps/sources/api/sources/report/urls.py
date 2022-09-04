from rest_framework import routers

from apps.sources.api.sources.report import views

router = routers.DefaultRouter()
router.register('reports', views.ReportViewSet)
