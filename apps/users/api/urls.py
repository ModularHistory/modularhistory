from django.urls import include, path, re_path

from apps.users.api import views
from apps.users.api.views import RegistrationView, SocialConnectView, SocialLoginView

app_name = 'users'

urlpatterns = [
    # https://github.com/iMerica/dj-rest-auth
    path('auth/', include('dj_rest_auth.urls')),
    re_path(r'auth/registration/?$', RegistrationView.as_view(), name='registration'),
    path('auth/<str:provider>/connect/', SocialConnectView.as_view(), name='social_connect'),
    path('auth/<str:provider>/', SocialLoginView.as_view(), name='social_login'),
    path(
        'me/social-accounts/', views.SocialAccountList.as_view(), name='social_account_list'
    ),
    path(
        'me/social-accounts/<int:pk>/disconnect/',
        views.SocialDisconnectView.as_view(),
        name='social_account_disconnect',
    ),
    path('me/', views.Me.as_view(), name='me'),
    path('<str:handle>/', views.ProfileView.as_view(), name='profile'),
]
