from dj_rest_auth.registration.views import SocialAccountDisconnectView, SocialAccountListView
from django.urls import include, path, re_path

from apps.users.api import views

app_name = 'users'

urlpatterns = [
    path(
        'me/social-accounts/',
        SocialAccountListView.as_view(),
        name='social_account_list',
    ),
    path(
        'me/social-accounts/<int:pk>/disconnect/',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect',
    ),
    path('me/', views.Me.as_view(), name='me'),
    path('<str:username>/', views.Profile.as_view(), name='profile'),
    re_path(r'auth/discord/?', views.DiscordLogin.as_view(), name='discord_login'),
    re_path(r'auth/facebook/?', views.FacebookLogin.as_view(), name='facebook_login'),
    re_path(r'auth/github/?', views.GithubLogin.as_view(), name='github_login'),
    re_path(r'auth/google/?', views.GoogleLogin.as_view(), name='google_login'),
    re_path(r'auth/twitter/?', views.TwitterLogin.as_view(), name='twitter_login'),
    path('auth/discord/connect/', views.DiscordConnect.as_view(), name='discord_connect'),
    path('auth/facebook/connect/', views.FacebookConnect.as_view(), name='facebook_connect'),
    path('auth/github/connect/', views.GithubConnect.as_view(), name='github_connect'),
    path('auth/google/connect/', views.GoogleConnect.as_view(), name='google_connect'),
    path('auth/twitter/connect/', views.TwitterLogin.as_view(), name='twitter_connect'),
    # https://github.com/iMerica/dj-rest-auth
    path('auth/', include('dj_rest_auth.urls')),
]
