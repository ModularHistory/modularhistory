"""API views for the account app."""

import datetime as dt
import json
import logging
from pprint import pprint

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
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

from apps.account.api import serializers
from apps.account.models import User

print(settings.ALLOWED_HOSTS)


class Me(generics.RetrieveAPIView):
    """API view for details of the current user."""

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        """Return the user object."""
        return self.request.user


class TokenViewWithCookie(TokenViewBase):
    """Base class for views obtaining/refreshing auth tokens."""

    def post(self, request, *args, **kwargs):
        """Make the post request to set the auth cookie."""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        # TODO: this should probably be pulled from the token exp
        expiration = dt.datetime.utcnow() + jwt_settings.REFRESH_TOKEN_LIFETIME

        response.set_cookie(
            settings.JWT_COOKIE_NAME,
            value=serializer.validated_data['refresh'],
            expires=expiration,
            secure=settings.JWT_COOKIE_SECURE,
            httponly=True,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )  # TODO: make sure this works; remove cookie setting from JS

        return response


class Login(TokenViewWithCookie):
    """View for obtaining an auth token."""

    serializer_class = serializers.TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        credentials = json.loads(request.body.decode('utf-8'))
        username, password = credentials.get('username'), credentials.get('password')
        return super().post(request=request, *args, **kwargs)


class RefreshToken(TokenViewWithCookie):
    """View for refreshing an auth token."""

    serializer_class = serializers.TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        """Make the post request to refresh the auth token."""
        response = super().post(request=request, *args, **kwargs)
        return response


class Logout(APIView):
    """View for logging out and deleting auth cookie."""

    def post(self, *args, **kwargs):
        """Make the post request to delete the auth cookie."""
        response = Response({})
        token = self.request.COOKIES.get(settings.JWT_COOKIE_NAME)
        refresh = RefreshTokenModel(token)
        refresh.blacklist()
        response.delete_cookie(settings.JWT_COOKIE_NAME)
        return response


@ensure_csrf_cookie
def set_csrf_token(request):
    """Ensure the CSRF cookie is set correctly."""
    return JsonResponse({"details": "CSRF cookie set"})


@require_POST
def log_in(request):
    """Log in with session-based auth."""
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return JsonResponse(
            {"errors": {"__all__": "Please enter both username and password"}},
            status=400,
        )
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"user": serializers.UserSerializer(user)})
    return JsonResponse(
        {"detail": "Invalid credentials"},
        status=400,
    )
