from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.log_in, name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('me/', views.Me.as_view(), name='me'),
    path('delete/', views.DeletionView.as_view(), name='delete'),
    path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/obtain/', views.Login.as_view(), name='token'),
    # path('token/refresh/', views.RefreshToken.as_view(), name='token_refresh'),
]
