from django.urls import include, path
from rest_framework import routers

from apps.search.api.todayinhistory import views

router = routers.DefaultRouter()
router.register('', views.TodayInHistoryViewSet)
