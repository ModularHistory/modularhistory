from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import View


class LoginView(auth_views.LoginView):
    template_name = 'account/login.html'


# class LogoutView(auth_views.LogoutView):
#     pass


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'account/password_change_form.html'


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'account/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    email_template_name = 'account/password_reset_email.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        context = {'form': form}
        return render(request, 'account/register.html', context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')


class ProfileView(LoginRequiredMixin, View):
    """Profile view"""
    def get(self, request):
        user = request.user
        context = {
            'user': user,
            'name': user.get_full_name(),
            'email': user.email,
            'profile_image_url': user.avatar.url if user.avatar else None,
        }
        return render(request, 'account/profile.html', context)
