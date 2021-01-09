from django.urls import path
from rest_framework import routers

from apps.quotes.api import views

router = routers.DefaultRouter()
router.register(r'quotes', views.QuoteViewSet)

app_name = 'quotes'

urlpatterns = [
    path('', views.QuoteListAPIView.as_view()),
]
