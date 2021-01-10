from django.urls import path

from rest_framework_simplejwt import views as jwt

app_name = 'account'

urlpatterns = [
    path('token/obtain/', jwt.TokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt.TokenRefreshView.as_view(), name='token_refresh'),
]
