from django.urls import path
from rest_framework import routers

from apps.occurrences.api import views

router = routers.DefaultRouter()
router.register(r'occurrences', views.OccurrenceViewSet)

app_name = 'occurrences'

urlpatterns = [
    path('', views.OccurrenceListAPIView.as_view(), name='index'),
    path('<slug:slug>/', views.OccurrenceAPIView.as_view()),
]
