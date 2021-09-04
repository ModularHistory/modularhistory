from django.urls import path, include
from rest_framework import routers

from apps.quotes.api import views

router = routers.DefaultRouter()
router.register('', views.QuoteViewSet)

app_name = 'quotes'

urlpatterns = [
    path('', include(router.urls)),
    path('<slug:slug>/', views.QuoteAPIView.as_view()),
]
