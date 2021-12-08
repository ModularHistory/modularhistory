from django.urls import include, path
from rest_framework import routers

from apps.entities.api import views

router = routers.DefaultRouter()
router.register('', views.EntityViewSet)

app_name = 'entities'

urlpatterns = [
    path(
        'instant_search/', views.EntityInstantSearchAPIView.as_view(), name='instant_search'
    ),
    path('', include(router.urls)),
]
