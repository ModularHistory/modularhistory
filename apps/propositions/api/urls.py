from django.urls import include, path
from rest_framework import routers

from apps.propositions.api import views

router = routers.DefaultRouter()
router.register('', views.PropositionViewSet)

app_name = 'propositions'

urlpatterns = [
    path('<slug:slug>/', views.PropositionAPIView.as_view()),
    path('', include(router.urls)),
    path('<slug:slug>/moderation/', views.PropositionModerationAPIView.as_view()),
]
