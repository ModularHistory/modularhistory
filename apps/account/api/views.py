"""API views for the account app."""

import datetime as dt
import logging
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken as RefreshTokenModel
from rest_framework_simplejwt.views import TokenViewBase

from apps.account.api import serializers


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
            serializer.validated_data['refresh'],
            expires=expiration,
            secure=settings.JWT_COOKIE_SECURE,
            httponly=True,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        print(response)
        print(f'>>> Successfully set cookie from {self.__class__}')

        return response


class Login(TokenViewWithCookie):
    """View for obtaining an auth token."""

    serializer_class = serializers.TokenObtainPairSerializer


class RefreshToken(TokenViewWithCookie):
    """View for refreshing an auth token."""

    serializer_class = serializers.TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request=request, *args, **kwargs)
        logging.info(f'>>>>>>>> {response}')
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
