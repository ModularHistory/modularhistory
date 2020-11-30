from django.urls import path

from apps.occurrences import views

app_name = 'occurrences'

urlpatterns = [
    path('', views.ListView.as_view(), name='index'),
    path('<int:pk>/part', views.DetailPartialView.as_view(), name='detail_part'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<slug:slug>/', views.DetailView.as_view(), name='detail_slug'),
]
