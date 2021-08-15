"""Serializers for the account app."""

from rest_framework.serializers import BooleanField, ModelSerializer

from apps.users.models import SocialAccount, User


class SocialAccountSerializer(ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = SocialAccount
        exclude = []


class UserSerializer(ModelSerializer):
    """Serializer for users."""

    isSuperuser = BooleanField(source='is_superuser')

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'avatar', 'isSuperuser']
