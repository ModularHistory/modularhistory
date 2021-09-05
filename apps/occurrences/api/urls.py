from django.urls import include, path
from rest_framework import routers

from apps.occurrences.api import views

router = routers.DefaultRouter()
router.register('', views.OccurrenceViewSet)

app_name = 'occurrences'

urlpatterns = [
    path('<slug:slug>/', views.OccurrenceAPIView.as_view()),
    path('', include(router.urls)),
]
