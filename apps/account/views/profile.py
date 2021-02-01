import logging
from typing import List, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from social_django.models import UserSocialAuth

from apps.account.models import User

LOGIN_PATH = '/login/'


class Provider:
    """Social auth provider."""

    key: str
    name: str
    domain: Optional[str]

    auth: Optional[str]
    handle: Optional[str]

    def __init__(self, key: str, name: str, domain: Optional[str] = None):
        """Construct a social auth provider object."""
        self.key = key
        self.name = name
        self.domain = domain or f'{name.lower()}.com'


class ProfileView(LoginRequiredMixin, View):
    """Profile view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the profile view upon request."""
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
        """Render the settings view upon request."""
        if isinstance(request.user, User):
            user: User = request.user
            social_auth_backends: List[Provider] = [
                Provider('google_oauth2', 'Google'),
                Provider('facebook', 'Facebook'),
                Provider('twitter', 'Twitter'),
                Provider('github', 'GitHub'),
            ]
            for backend in social_auth_backends:
                try:
                    auth = user.social_auth.get(provider=backend.key)
                    backend.auth = auth
                    backend.handle = get_user_handle_from_auth(auth)
                except UserSocialAuth.DoesNotExist:
                    pass
                except Exception as err:
                    logging.error(
                        f'Error processing social auth integration: {type(err)}: {err}'
                    )

            can_disconnect = user.social_auth.count() > 1 or user.has_usable_password()

            context = {
                'profile_image': user.avatar or 'nobody_m.jpg',
                'social_auth_backends': social_auth_backends,
                'can_disconnect': can_disconnect,
            }
            return render(request, 'account/settings.html', context)
        return HttpResponseRedirect(LOGIN_PATH)


def get_user_handle_from_auth(auth: Optional[UserSocialAuth]) -> Optional[str]:
    """Given a social auth object, return the user's social media handle/username."""
    if auth:
        provider = auth.provider
        if provider == 'twitter':
            return auth.extra_data['access_token']['screen_name']
        elif provider == 'facebook':
            return auth.extra_data['id']
        # TODO: handle other backends
    return None
