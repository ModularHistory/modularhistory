from django.urls import include, path, re_path

from apps.users.api import views
from apps.users.api.views import (
    SocialConnectView,
    SocialLoginView,
    disconnect_social_account,
    list_social_accounts,
    register,
    resend_email_verification,
    verify_email,
)

app_name = 'users'

urlpatterns = [
    re_path(r'auth/registration/?$', register, name='registration'),
    re_path(r'email-verification/?$', verify_email),
    path('auth/resend-email/', resend_email_verification),
    path('auth/<str:provider>/connect/', SocialConnectView.as_view(), name='social_connect'),
    # https://github.com/iMerica/dj-rest-auth
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/<str:provider>/', SocialLoginView.as_view(), name='social_login'),
    path('me/social-accounts/', list_social_accounts),
    path('me/social-accounts/<int:pk>/disconnect/', disconnect_social_account),
    path('me/', views.Me.as_view(), name='me'),
    path('<str:handle>/', views.ProfileView.as_view(), name='profile'),
]
