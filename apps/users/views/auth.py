import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View

from apps.users.forms import LoginForm, RegistrationForm
from apps.users.models import User


class LoginView(auth_views.LoginView):
    """Login view."""

    form_class = LoginForm
    template_name = 'users/login.html'


LogoutView = auth_views.LogoutView


class RegisterView(View):
    """Account registration view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the registration view when the page is requested."""
        form: RegistrationForm = RegistrationForm()
        context = {'form': form}
        return render(request, 'users/register.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Respond to registration form submission."""
        form: RegistrationForm = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if isinstance(user, User):
                login(request, user)
                return redirect('/')
            else:
                logging.error(f'Unexpected authentication result: {type(user)}: {user}')
        return render(request, 'users/register.html', {'form': form})
