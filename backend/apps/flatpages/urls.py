from django.urls import path

from apps.flatpages import views

urlpatterns = [
    path('<path:path>', views.flatpage, name='flatpage'),
]
