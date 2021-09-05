from django.urls import include, path
from rest_framework import routers

from apps.quotes.api import views

router = routers.DefaultRouter()
router.register('', views.QuoteViewSet)

app_name = 'quotes'

urlpatterns = [
    path('', include(router.urls)),
]
