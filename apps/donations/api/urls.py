from django.urls import path
from rest_framework import routers

from apps.donations.api import views

router = routers.DefaultRouter()
# router.register(r'donations', views.EntityViewSet)

app_name = 'donations'

urlpatterns = [
    path('token/', views.get_token),
    path('process/', views.process),
    # path('partial/', views.EntityPartialAPIView.as_view()),
]
