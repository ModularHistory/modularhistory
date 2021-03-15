from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from apps.users.models import User

LOGIN_PATH = '/login/'


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
            return render(request, 'users/profile.html', context)
        return HttpResponseRedirect(LOGIN_PATH)
