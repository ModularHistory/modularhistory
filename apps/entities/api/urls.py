from django.urls import path, include
from rest_framework import routers

from apps.entities.api import views

router = routers.DefaultRouter()
router.register(r'', views.EntityViewSet)

app_name = 'entities'

urlpatterns = [
    path('', include(router.urls)),
    path('instant_search/', views.EntityInstantSearchAPIView.as_view()),
]
