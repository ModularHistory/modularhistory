from rest_framework import routers

from apps.sources.api.sources.publications import views

router = routers.DefaultRouter()
router.register('publications', views.PublicationViewSet)
router.register('webpages', views.WebpageViewSet)
router.register('websites', views.WebsiteViewSet)
