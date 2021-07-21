from django.urls import include, path

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]
