from django.urls import path

from postulations import views

app_name = 'postulations'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/part', views.DetailPartView.as_view(), name='detail'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
]
