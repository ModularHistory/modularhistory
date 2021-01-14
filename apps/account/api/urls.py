from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('me/', views.Me.as_view(), name='me'),
    path('token/obtain/', views.Login.as_view(), name='token'),
    path('token/refresh/', views.RefreshToken.as_view(), name='token-refresh'),
    path('logout/', views.Logout.as_view(), name='logout'),
]
