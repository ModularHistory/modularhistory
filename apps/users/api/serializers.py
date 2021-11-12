"""Serializers for the account app."""

from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.users.models import SocialAccount, User

if TYPE_CHECKING:
    from rest_framework.request import Request


class SocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = SocialAccount
        exclude = []


class SocialLoginSerializer(serializers.Serializer):
    """Serializer for social login."""

    access_token = serializers.CharField(required=False, allow_blank=True)
    id_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs: dict):
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


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = User
        fields = ['id', 'handle', 'name', 'email', 'avatar', 'is_superuser']


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate_email(self, email: str):
        # email = get_adapter().clean_email(email)
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _('A user is already registered with this e-mail address.'),
            )
        return email

    def validate_password(self, password: str):
        return password
        # return get_adapter().clean_password(password)

    def validate(self, data: dict):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password': self.validated_data.get('password', ''),
            'password_confirmation': self.validated_data.get('password_confirmation', ''),
        }

    def save(self, *args, **kwargs):
        self.cleaned_data = self.get_cleaned_data()
        email_address = self.cleaned_data['email']
        user: User = User(
            email=email_address,
            username=email_address,
        )
        user.set_password(self.cleaned_data['password'])
        user.save()
        # setup_user_email(request, user, [])
        return user


class EmailVerificationSerializer(serializers.Serializer):
    key = serializers.CharField()


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
