from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

app_name = 'account'

urlpatterns = [
    # https://github.com/iMerica/dj-rest-auth
    path('auth/', include('dj_rest_auth.urls')),
    path('login/', views.log_in, name='login'),
    # path('logout/', views.Logout.as_view(), name='logout'),
    path('me/', views.Me.as_view(), name='me'),
    path('delete/', views.DeletionView.as_view(), name='delete'),
    path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
