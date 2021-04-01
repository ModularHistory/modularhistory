"""API views for the account app."""

from allauth.socialaccount.providers.discord.views import DiscordOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import (
    SocialConnectView,
    SocialLoginView as BaseSocialLoginView,
)
from dj_rest_auth.social_serializers import (
    TwitterConnectSerializer,
    TwitterLoginSerializer,
)
import logging
import json
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse, HttpRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from typing import TYPE_CHECKING, Optional
from apps.users.api import serializers
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from apps.users.models import User
from allauth.socialaccount.models import SocialAccount


class SocialLoginView(BaseSocialLoginView):
    """Base class for social login views."""

    user: 'User'

    def post(self, request: Request, *args, **kwargs):
        """Override the post method to save data from the social media account."""
        response = super().post(request, *args, **kwargs)
        user_data = request.data.get('user')
        if self.user and user_data:
            email = user_data.get('email')
            if email and not self.user.email:
                try:
                    # Find and update an existing user with the email address.
                    user: User = User.objects.get(email=email)
                    print(f'Found existing user with email address {email}')
                    try:
                        for social_account in SocialAccount.objects.filter(
                            user_id=self.user.pk
                        ):
                            social_account.user = user
                            social_account.save()
                    except Exception as err:
                        # TODO: Catch a more specific Exception type
                        logging.error(err)
                    # TODO: add celery task to delete
                    self.user.delete()
                except ObjectDoesNotExist:
                    self.user.email = email
                    self.user.save()
            # TODO: Update name and image appropriately.
            # image = user_data.get('image')
            # name = user_data.get('name')
        return response


class DiscordMixin:
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html."""

    adapter_class = DiscordOAuth2Adapter
    # Callback URL must match the setting in Discord:
    # https://discord.com/developers/applications/826485521151819786/oauth2
    callback_url = f'{settings.BASE_URL}/api/auth/callback/discord/'
    client_class = OAuth2Client


class DiscordLogin(DiscordMixin, SocialLoginView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html."""

    pass


class DiscordConnect(DiscordMixin, SocialConnectView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

    pass


class FacebookMixin:
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#facebook."""

    adapter_class = FacebookOAuth2Adapter


class FacebookLogin(FacebookMixin, SocialLoginView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#facebook."""

    pass


class FacebookConnect(FacebookMixin, SocialConnectView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

    pass


class GithubMixin:
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#github."""

    adapter_class = GitHubOAuth2Adapter
    # Callback URL must match the setting in GitHub:
    # https://github.com/organizations/ModularHistory/settings/applications/1489184
    callback_url = f'{settings.BASE_URL}/api/auth/callback/github/'
    client_class = OAuth2Client


class GithubLogin(GithubMixin, SocialLoginView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#github."""

    pass


class GithubConnect(GithubMixin, SocialConnectView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

    pass


class GoogleMixin:
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html."""

    adapter_class = GoogleOAuth2Adapter
    # Callback URL must match the setting in Google:
    # TODO: paste Google settings URL here.
    callback_url = f'{settings.BASE_URL}/api/auth/callback/google/'
    client_class = OAuth2Client


class GoogleLogin(GoogleMixin, SocialLoginView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html."""

    pass


class GoogleConnect(GoogleMixin, SocialConnectView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

    pass


class TwitterMixin:
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#twitter."""

    adapter_class = TwitterOAuthAdapter


class TwitterLogin(TwitterMixin, SocialLoginView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#twitter."""

    serializer_class = TwitterLoginSerializer


class TwitterConnect(TwitterMixin, SocialConnectView):
    """See https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

    serializer_class = TwitterConnectSerializer


class Me(generics.RetrieveAPIView):
    """API view for details of the current user."""

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        """
        Return the user object.

        https://www.django-rest-framework.org/api-guide/generic-views/#get_objectself
        """
        return self.request.user


class DeletionView(generics.DestroyAPIView):
    """Delete a user's data."""

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    lookup_field = 'email'
    queryset = get_user_model().objects.all()

    def get_object(self):
        """
        Return the user object to be deleted.

        https://www.django-rest-framework.org/api-guide/generic-views/#get_objectself
        """
        user: 'User' = self.request.user  # type: ignore
        try:
            instance = self.queryset.get(email=user.email)
            return instance
        except ObjectDoesNotExist:
            raise Http404


@ensure_csrf_cookie
def set_csrf_token(request):
    """Ensure the CSRF cookie is set correctly."""
    return JsonResponse({"details": "CSRF cookie set"})
