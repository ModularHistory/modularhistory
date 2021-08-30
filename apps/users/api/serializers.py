"""Serializers for the account app."""

from rest_framework.serializers import ModelSerializer

from apps.users.models import SocialAccount, User


class SocialAccountSerializer(ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = SocialAccount
        exclude = []


class UserSerializer(ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = User
        fields = ['id', 'handle', 'name', 'email', 'avatar', 'is_superuser']
