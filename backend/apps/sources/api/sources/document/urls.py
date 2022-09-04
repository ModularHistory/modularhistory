from rest_framework import routers

from apps.sources.api.sources.document import views
from apps.sources.api.sources.document.affidavit import views as affidavit_views
from apps.sources.api.sources.document.collection import views as collection_views
from apps.sources.api.sources.document.correspondence import views as correspondence_views

router = routers.DefaultRouter()
router.register('repositories', collection_views.RepositoryViewSet)
router.register('collections', collection_views.CollectionViewSet)
router.register('affidavits', affidavit_views.AffidavitViewSet)
router.register('correspondences', correspondence_views.CorrespondenceViewSet)
router.register('documents', views.DocumentViewSet)
