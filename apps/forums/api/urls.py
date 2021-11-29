from django.urls import include, path
from rest_framework import routers

from apps.forums.api import views

thread_router = routers.DefaultRouter()
thread_router.register('', views.ThreadViewSet)

post_router = routers.DefaultRouter()
post_router.register('', views.PostViewSet)

app_name = 'forums'

urlpatterns = [
    path('threads/', include(thread_router.urls)),
    path('posts/', include(post_router.urls)),
]
