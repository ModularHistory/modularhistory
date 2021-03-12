"""API views for the account app."""

import datetime as dt
import json

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import SocialConnectView, SocialLoginView
from dj_rest_auth.social_serializers import (
    TwitterConnectSerializer,
    TwitterLoginSerializer,
)
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken as RefreshTokenModel
from rest_framework_simplejwt.views import TokenViewBase

from apps.users.api import serializers

User = get_user_model()


class FacebookMixin:
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#facebook."""

    adapter_class = FacebookOAuth2Adapter


class FacebookLogin(FacebookMixin, SocialLoginView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#facebook."""

    pass


class FacebookConnect(FacebookMixin, SocialConnectView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""

    pass


class TwitterMixin:
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#twitter."""

    adapter_class = TwitterOAuthAdapter


class TwitterLogin(TwitterMixin, SocialLoginView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#twitter."""

    serializer_class = TwitterLoginSerializer


class TwitterConnect(TwitterMixin, SocialConnectView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""

    serializer_class = TwitterConnectSerializer


class GithubMixin:
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#github."""

    adapter_class = GitHubOAuth2Adapter
    callback_url = None  # CALLBACK_URL_YOU_SET_ON_GITHUB
    client_class = OAuth2Client


class GithubLogin(GithubMixin, SocialLoginView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#github."""

    pass


class GithubConnect(GithubMixin, SocialConnectView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""

    pass


class Me(generics.RetrieveAPIView):
    """API view for details of the current user."""

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        """Return the user object."""
        return self.request.user


# class TokenViewWithCookie(TokenViewBase):
#     """Base class for views obtaining/refreshing auth tokens."""

#     def post(self, request, *args, **kwargs):
#         """Make the post request to set the auth cookie."""
#         serializer = self.get_serializer(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)
#         except TokenError as e:
#             raise InvalidToken(e.args[0])

#         response = Response(serializer.validated_data, status=status.HTTP_200_OK)

#         # TODO: this should probably be pulled from the token exp
#         expiration = dt.datetime.utcnow() + jwt_settings.REFRESH_TOKEN_LIFETIME

#         response.set_cookie(
#             settings.JWT_COOKIE_NAME,
#             value=serializer.validated_data['refresh'],
#             expires=expiration,
#             secure=settings.JWT_COOKIE_SECURE,
#             httponly=True,
#             samesite=settings.JWT_COOKIE_SAMESITE,
#         )  # TODO: make sure this works; remove cookie setting from JS

#         return response


# class Login(TokenViewWithCookie):
#     """View for obtaining an auth token."""

#     serializer_class = serializers.TokenObtainPairSerializer

#     def post(self, request, *args, **kwargs):
#         # credentials = json.loads(request.body.decode('utf-8'))  # noqa: E500
#         # username, password = credentials.get('username'), credentials.get('password')  # noqa: E500
#         return super().post(request=request, *args, **kwargs)


# class RefreshToken(TokenViewWithCookie):
#     """View for refreshing an auth token."""

#     serializer_class = serializers.TokenRefreshSerializer

#     def post(self, request, *args, **kwargs):
#         """Make the post request to refresh the auth token."""
#         response = super().post(request=request, *args, **kwargs)
#         return response


# class Logout(APIView):
#     """View for logging out and deleting auth cookie."""

#     def post(self, *args, **kwargs):
#         """Make the post request to delete the auth cookie."""
#         response = Response({})
#         token = self.request.COOKIES.get(settings.JWT_COOKIE_NAME)
#         refresh = RefreshTokenModel(token)
#         refresh.blacklist()
#         response.delete_cookie(settings.JWT_COOKIE_NAME)
#         return response


@ensure_csrf_cookie
def set_csrf_token(request):
    """Ensure the CSRF cookie is set correctly."""
    return JsonResponse({"details": "CSRF cookie set"})


@require_POST
def log_in(request):
    """Log in with JWT and session-based auth."""
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return JsonResponse(
            {"errors": {"__all__": "Please enter both username and password"}},
            status=400,
        )
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse(
            {"detail": "Invalid credentials"},
            status=400,
        )
    login(request, user)
    return JsonResponse({"user": serializers.UserSerializer(user)})


class DeletionView(generics.DestroyAPIView):
    """Delete a user's data."""

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    lookup_field = 'email'
    queryset = User.objects.all()

    def get_object(self):
        user: User = self.request.user  # type: ignore
        try:
            instance = self.queryset.get(email=user.email)
            return instance
        except User.DoesNotExist:
            raise Http404
