from dj_rest_auth.registration.views import (
    SocialAccountDisconnectView,
    SocialAccountListView,
)
from django.urls import include, path, re_path

from apps.users.api import views

app_name = 'users'

urlpatterns = [
    path(
        'me/socialaccounts/',
        SocialAccountListView.as_view(),
        name='social_account_list',
    ),
    path(
        'me/socialaccounts/<int:pk>/disconnect/',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect',
    ),
    path('me/', views.Me.as_view(), name='me'),
    re_path(r'auth/discord/?', views.DiscordLogin.as_view(), name='discord_login'),
    re_path(r'auth/facebook/?', views.FacebookLogin.as_view(), name='facebook_login'),
    re_path(r'auth/github/?', views.GithubLogin.as_view(), name='github_login'),
    re_path(r'auth/google/?', views.GoogleLogin.as_view(), name='google_login'),
    re_path(r'auth/twitter/?', views.TwitterLogin.as_view(), name='twitter_login'),
    # https://github.com/iMerica/dj-rest-auth
    path('auth/', include('dj_rest_auth.urls')),
]
