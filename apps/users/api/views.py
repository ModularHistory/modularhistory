"""API views for the account app."""

from typing import TYPE_CHECKING

from dj_rest_auth.views import LoginView
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import generics, permissions
from rest_framework.views import APIView

from apps.users.api.serializers import (
    RegistrationSerializer,
    SocialAccountSerializer,
    SocialLoginSerializer,
    UserSerializer,
)
from apps.users.models import SocialAccount, User

if TYPE_CHECKING:
    from rest_framework.request import Request

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password1', 'password2'),
)


class RegistrationView(generics.CreateAPIView):
    """API view for registering a new user account with credentials."""

    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'dj_rest_auth'

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SocialAccountList(generics.ListAPIView):
    """API view for listing a user's connected social accounts."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialAccountSerializer

    def get_queryset(self):  # noqa: D102
        return SocialAccount.objects.filter(user=self.request.user)


class SocialConnectView(APIView):
    """API view for connecting a social account."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: 'Request', *args, **kwargs):
        """Save data from the social media account."""


class SocialDisconnectView(generics.DestroyAPIView):
    """API view for connecting a social account."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: 'Request', *args, **kwargs):
        """Disconnect the social media account."""


class SocialLoginView(LoginView):
    """API view for logging in via a social account."""

    serializer_class = SocialLoginSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """API view for details of the current user."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    lookup_field = 'handle'
    queryset = User.objects.all()


class Me(ProfileView):
    """API view for details of the current user."""

    permission_classes = (permissions.IsAuthenticated,)

    # https://www.django-rest-framework.org/api-guide/generic-views/#get_object
    def get_object(self, *args, **kwargs):
        """Return the user object."""
        return self.request.user


class DeletionView(generics.DestroyAPIView):
    """API view for deleting a user's data."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    lookup_field = 'email'
    queryset = get_user_model().objects.all()

    # https://www.django-rest-framework.org/api-guide/generic-views/#get_object
    def get_object(self):
        """Return the user object to be deleted."""
        user: 'User' = self.request.user  # type: ignore
        try:
            instance = self.queryset.get(email=user.email)
            return instance
        except ObjectDoesNotExist:
            raise Http404


@ensure_csrf_cookie
def set_csrf_token(request):
    """Ensure the CSRF cookie is set correctly."""
    return JsonResponse({'details': 'CSRF cookie set'})
