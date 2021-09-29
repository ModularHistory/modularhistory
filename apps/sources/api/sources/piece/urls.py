from rest_framework import routers

from apps.sources.api.sources.piece import views

router = routers.DefaultRouter()
router.register('pieces', views.PieceViewSet)
