from django.urls import include, path

app_name = 'users'

urlpatterns = [
    # https://github.com/iMerica/dj-rest-auth
    path('auth/', include('dj_rest_auth.urls')),
]
