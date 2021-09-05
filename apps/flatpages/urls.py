from django.urls import path

from apps.flatpages import views

urlpatterns = [
    path('<path:url>', views.flatpage, name='flatpage'),
]
