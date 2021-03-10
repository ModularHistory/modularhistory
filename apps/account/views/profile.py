import logging
from typing import List, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

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
