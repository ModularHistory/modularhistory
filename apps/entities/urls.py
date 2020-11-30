from django.urls import path
from rest_framework import routers

from apps.entities import views

router = routers.DefaultRouter()
router.register(r'entities', views.EntityViewSet)

app_name = 'entities'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/part', views.DetailPartView.as_view(), name='detail'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<slug:slug>/', views.DetailView.as_view(), name='detail_slug'),
    path('api/entities/', views.EntityListAPIView.as_view()),
]
