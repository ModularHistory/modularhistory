from django.urls import include, path
from rest_framework import routers

from apps.collections.api import views

router = routers.DefaultRouter()
router.register('', views.CollectionViewSet)

app_name = 'collections'

urlpatterns = [
    path('add_items/', views.CollectionAddItemsView.as_view(), name='add_items'),
    path('remove_items/', views.CollectionRemoveItemsView.as_view(), name='remove_items'),
    path('', include(router.urls)),
]
