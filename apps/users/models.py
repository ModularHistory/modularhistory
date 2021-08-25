import logging
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.core.files import File
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_cryptography.fields import encrypt

from core.fields.file_field import upload_to

AVATAR_QUALITY: int = 70
AVATAR_WIDTH: int = 200
AVATAR_HEIGHT: int = AVATAR_WIDTH


class SocialAccount(models.Model):
    """A social media account."""

    class Provider(models.TextChoices):
        DISCORD = 'discord', 'Discord'
        FACEBOOK = 'facebook', 'Facebook'
        GITHUB = 'github', 'GitHub'
        GOOGLE = 'google', 'Google'
        TWITTER = 'twitter', 'Twitter'

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_accounts',
    )
    provider = models.CharField(max_length=10, choices=Provider.choices)
    uid = models.CharField(max_length=200)
    access_token = encrypt(models.CharField(max_length=200))

    class Meta:
        unique_together = [('user', 'provider'), ('provider', 'uid')]

    def __str__(self) -> str:
        return f'{self.provider} account {self.uid}'


class UserManager(BaseUserManager):
    """Manager for users."""


def get_handle_base(instance: 'User') -> str:
    """Return the value to use as the base for the user's default handle."""
    if instance.name:
        return instance.name
    elif instance.email:
        return instance.email.split('@')[0]
    else:
        return instance.username


def handlify(value: str) -> str:
    """Modify the value to be in the appropriate format for a handle."""
    return value.replace(' ', '')


class User(AbstractUser):
    """A user of ModularHistory."""

    email = models.EmailField(verbose_name=_('email address'), unique=True)
    handle = AutoSlugField(
        verbose_name=_('handle'),
        populate_from=get_handle_base,
        slugify=handlify,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name=_('avatar'),
        null=True,
        blank=True,
        upload_to=upload_to('users/avatars'),
    )
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    force_password_change = models.BooleanField(
        'Prompt user to change password upon first login', default=False
    )

    objects: UserManager = UserManager()

    def __str__(self) -> str:
        """Return a string representation of the user."""
        return self.name or self.username

    @property
    def name(self) -> str:
        """Return the user's name."""
        return self.get_full_name()

    def get_handle_base(self) -> str:
        """Return the value to use as the base for the user's default handle."""
        return get_handle_base(self)

    def update_avatar(self, url: str):
        """Update the user's avatar with the image located at the given URL."""
        if self.avatar:
            logging.info(f'{self} already has an avatar: {self.avatar}')
            # TODO: check if image has been updated
        else:
            logging.info(f'{self} has no profile image.')
            img_temp = NamedTemporaryFile(delete=True)
            # TODO: Use requests instead of urllib?
            img_temp.write(urlopen(url).read())  # noqa: S310
            img_temp.flush()
            self.avatar.save(f'{self.pk}', File(img_temp))
