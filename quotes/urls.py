from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/part', views.DetailPartView.as_view(), name='detail_part'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
]
