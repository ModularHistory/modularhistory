from rest_framework import routers

from apps.sources.api.sources.document import views
from apps.sources.api.sources.document.collection import views as collection_views

router = routers.DefaultRouter()
router.register('repositories', collection_views.RepositoryViewSet)
router.register('collections', collection_views.CollectionViewSet)
router.register('documents', views.DocumentViewSet)
