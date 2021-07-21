"""Serializers for the account app."""

from rest_framework.serializers import BooleanField, ModelSerializer

from apps.users.models import User


class UserSerializer(ModelSerializer):
    """Serializer for users."""

    isSuperuser = BooleanField(source='is_superuser')

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'avatar', 'isSuperuser']
