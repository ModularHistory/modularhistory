"""API views for the account app."""


from typing import TYPE_CHECKING

from dj_rest_auth.views import LoginView
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions, serializers
from rest_framework.views import APIView

from apps.users.api.serializers import SocialAccountSerializer, UserSerializer
from apps.users.models import SocialAccount, User

if TYPE_CHECKING:
    from rest_framework.request import Request


class SocialAccountList(generics.ListAPIView):
    """API view for listing a user's connected social accounts."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialAccountSerializer

    def get_queryset(self):  # noqa: D102
        return SocialAccount.objects.filter(user=self.request.user)


class SocialConnect(APIView):
    """API view for connecting a social account."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: 'Request', *args, **kwargs):
        """Save data from the social media account."""


class SocialDisconnect(generics.DestroyAPIView):
    """API view for connecting a social account."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: 'Request', *args, **kwargs):
        """Disconnect the social media account."""


class SocialLoginSerializer(serializers.Serializer):
    """Serializer for social login."""

    access_token = serializers.CharField(required=False, allow_blank=True)
    id_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        request: 'Request' = self.context['request']
        provider = request.data['account']['provider']
        credentials = request.data['credentials']
        uid = credentials['user']['id']
        access_token = credentials['access_token']
        if SocialAccount.objects.filter(provider=provider, uid=uid).exists():
            account = SocialAccount.objects.filter(provider=provider, uid=uid).first()
            account.access_token = access_token
            account.save()
        else:
            account = SocialAccount(provider=provider, uid=uid, access_token=access_token)
            email = credentials['user'].get('email')
            if email and User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                account.user = user
            else:
                account.user = User.objects.create(username=email, email=email)
            account.save()
        attrs['user'] = account.user
        return attrs


class SocialLogin(LoginView):
    """API view for logging in via a social account."""

    serializer_class = SocialLoginSerializer


class Profile(generics.RetrieveUpdateAPIView):
    """API view for details of the current user."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    lookup_field = 'handle'
    queryset = User.objects.all()


class Me(Profile):
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
