from django.urls import path

from apps.entities.api import views

app_name = 'cms'

urlpatterns = [
    path('<str:directory>/<int:id>/', views.EntityListAPIView.as_view()),
]
