from django.urls import include, path

from apps.users.api import views

app_name = 'users'

urlpatterns = [
    # https://github.com/iMerica/dj-rest-auth
    path('auth/', include('dj_rest_auth.urls')),
    path(
        'auth/<str:provider>/connect/',
        views.SocialConnect.as_view(),
        name='social_connect',
    ),
    path('auth/<str:provider>/', views.SocialLogin.as_view(), name='social_login'),
    path(
        'me/social-accounts/',
        views.SocialAccountList.as_view(),
        name='social_account_list',
    ),
    path(
        'me/social-accounts/<int:pk>/disconnect/',
        views.SocialDisconnect.as_view(),
        name='social_account_disconnect',
    ),
    path('me/', views.Me.as_view(), name='me'),
    path('<str:handle>/', views.Profile.as_view(), name='profile'),
]
