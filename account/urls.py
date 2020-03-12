from django.urls import include, path, re_path

from . import views

urlpatterns = [
    re_path(r'login/?', views.LoginView.as_view(), name='login'),
    re_path(r'register/?', views.RegisterView.as_view(), name='register'),
    # accounts/logout/ [name='logout']
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeView.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetView.as_view(), name='password_reset_done'),
    re_path(r'profile/?', views.ProfileView.as_view(), name='profile'),
    re_path(r'settings/?', views.SettingsView.as_view(), name='settings'),
    # accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # accounts/reset/done/ [name='password_reset_complete']
    path('', include('django.contrib.auth.urls')),
]
