from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from social_django.models import UserSocialAuth

from account.models import User

LOGIN_PATH = '/login/'


class ProfileView(LoginRequiredMixin, View):
    """Profile view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """TODO: add docstring."""
        if isinstance(request.user, User):
            user: User = request.user
            context = {
                'user': user,
                'name': user.get_full_name(),
                'email': user.email,
                'profile_image_url': user.avatar.url if user.avatar else None,
            }
            return render(request, 'account/profile.html', context)
        return HttpResponseRedirect(LOGIN_PATH)


class SettingsView(LoginRequiredMixin, View):
    """Account settings view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """TODO: add docstring."""
        if isinstance(request.user, User):
            user: User = request.user
            social_auth_backends = [
                {'provider': 'google_oauth2', 'name': 'Google', 'auth': None, 'handle': None},
                {'provider': 'facebook', 'name': 'Facebook', 'auth': None, 'handle': None},
                {'provider': 'twitter', 'name': 'Twitter', 'auth': None, 'handle': None},
                {'provider': 'github', 'name': 'GitHub', 'auth': None, 'handle': None},
            ]
            for backend in social_auth_backends:
                backend_name = backend['name']
                try:
                    auth = user.social_auth.get(provider=backend['provider'])
                    backend['auth'] = auth
                    backend['handle'] = get_user_handle_from_auth(auth)
                except UserSocialAuth.DoesNotExist:
                    pass
                except Exception as error:
                    print(f'Error processing social auth integration: {type(error)}: {error}')
                backend['domain'] = f'{backend_name.lower()}.com'

            can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

            context = {
                'user': user,
                'name': user.get_full_name(),
                'email': user.email,
                'profile_image': user.avatar or 'nobody_m.jpg',
                'social_auth_backends': social_auth_backends,
                'can_disconnect': can_disconnect,
            }
            return render(request, 'account/settings.html', context)
        return HttpResponseRedirect(LOGIN_PATH)


def get_user_handle_from_auth(auth: Optional[UserSocialAuth]) -> Optional[str]:
    """Given a social auth object, return the user's social media handle/username."""
    provider = auth.provider
    if provider == 'twitter':
        return auth.extra_data['access_token']['screen_name']
    elif provider == 'facebook':
        return auth.extra_data['id']
    # TODO: handle other backends
    return None
