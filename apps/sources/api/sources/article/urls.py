from rest_framework import routers

from apps.sources.api.sources.article import views

router = routers.DefaultRouter()
router.register('articles', views.ArticleViewSet)
