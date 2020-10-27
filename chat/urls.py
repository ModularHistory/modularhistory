"""URL config for chat app."""

from django.urls import path

from chat import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
]
