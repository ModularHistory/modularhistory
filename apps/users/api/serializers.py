"""Serializers for the account app."""

import logging
from typing import TYPE_CHECKING

import serpy

if TYPE_CHECKING:
    from apps.users.models import User


class UserSerializer(serpy.Serializer):
    """Serializer for users."""

    id = serpy.Field()
    username = serpy.Field()
    avatar = serpy.MethodField('get_avatar')
    name = serpy.Field()
    email = serpy.Field()
    is_superuser = serpy.BoolField()
    # 'is_active',
    # 'date_joined',
    # 'last_login',

    def get_avatar(self, instance: 'User'):
        """Return the entity's death date, serialized."""
        try:
            return instance.avatar.url if instance.avatar else None
        except Exception as err:
            logging.error(f'{err}')
        return None
