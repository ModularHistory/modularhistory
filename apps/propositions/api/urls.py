from django.urls import path
from rest_framework import routers

from apps.propositions.api import views

router = routers.DefaultRouter()
router.register(r'propositions', views.PropositionViewSet)

app_name = 'propositions'

urlpatterns = [
    path('', views.PropositionListAPIView.as_view()),
]
