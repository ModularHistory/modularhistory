from rest_framework import routers

from apps.sources.api.sources.entry import views

router = routers.DefaultRouter()
router.register('entries', views.EntryViewSet)
