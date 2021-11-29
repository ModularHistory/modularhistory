"""API views for the account app."""

from typing import TYPE_CHECKING

from dj_rest_auth.views import LoginView
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import generics, permissions, status
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import (
    EmailVerificationSerializer,
    RegistrationSerializer,
    ResendEmailVerificationSerializer,
    SocialAccountSerializer,
    SocialLoginSerializer,
    UserSerializer,
)
from apps.users.models import EmailAddress, EmailConfirmation, SocialAccount, User

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save(self.request)
        email: EmailAddress = EmailAddress.objects.get_or_create(user=user, email=user.email)[
            0
        ]
        email.send_confirmation()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


register = RegistrationView.as_view()


class EmailVerificationView(APIView):
    """API view for email address verification."""

    permission_classes = (permissions.AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return EmailVerificationSerializer(*args, **kwargs)

    def get(self, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({'detail': _('ok')}, status=status.HTTP_200_OK)

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        emailconfirmation = EmailConfirmation.from_key(key)
        if not emailconfirmation:
            raise Http404()
        return emailconfirmation


verify_email = EmailVerificationView.as_view()


class ResendEmailVerificationView(generics.CreateAPIView):
    """API view for resending an email address verification request."""

    permission_classes = (permissions.AllowAny,)
    serializer_class = ResendEmailVerificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email: EmailAddress = EmailAddress.objects.get(**serializer.validated_data)
        if not email:
            raise ValidationError('Account does not exist')
        if email.verified:
            raise ValidationError('Account is already verified')
        email.send_confirmation()
        return Response({'detail': _('ok')}, status=status.HTTP_200_OK)


resend_email_verification = ResendEmailVerificationView.as_view()


class SocialAccountListView(generics.ListAPIView):
    """API view for listing a user's connected social accounts."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialAccountSerializer

    def get_queryset(self):  # noqa: D102
        return SocialAccount.objects.filter(user=self.request.user)


list_social_accounts = SocialAccountListView.as_view()


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


disconnect_social_account = SocialDisconnectView.as_view()


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
def set_csrf_token(request) -> JsonResponse:
    """Ensure the CSRF cookie is set correctly."""
    return JsonResponse({'details': 'CSRF cookie set'})
