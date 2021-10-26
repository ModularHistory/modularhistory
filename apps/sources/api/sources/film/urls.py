from rest_framework import routers

from apps.sources.api.sources.film import views

router = routers.DefaultRouter()
router.register('films', views.FilmViewSet)
