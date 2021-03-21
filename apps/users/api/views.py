"""API views for the account app."""

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import SocialConnectView, SocialLoginView
from dj_rest_auth.social_serializers import (
    TwitterConnectSerializer,
    TwitterLoginSerializer,
)
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.users.api import serializers

User = get_user_model()


class FacebookMixin:
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#facebook."""

    adapter_class = FacebookOAuth2Adapter


class FacebookLogin(FacebookMixin, SocialLoginView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#facebook."""

    pass


class FacebookConnect(FacebookMixin, SocialConnectView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

    pass


class TwitterMixin:
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#twitter."""

    adapter_class = TwitterOAuthAdapter


class TwitterLogin(TwitterMixin, SocialLoginView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#twitter."""

    serializer_class = TwitterLoginSerializer


class TwitterConnect(TwitterMixin, SocialConnectView):
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

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
    """https://dj-rest-auth.readthedocs.io/en/latest/installation.html#additional-social-connect-views."""  # noqa: E501

    pass


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
    queryset = User.objects.all()

    def get_object(self):
        """
        Return the user object to be deleted.

        https://www.django-rest-framework.org/api-guide/generic-views/#get_objectself
        """
        user: User = self.request.user  # type: ignore
        try:
            instance = self.queryset.get(email=user.email)
            return instance
        except User.DoesNotExist:
            raise Http404
