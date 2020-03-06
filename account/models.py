from typing import Any, Tuple

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class UserManager(BaseUserManager):
    def get_by_natural_key(self, *args):
        fields = self.model.natural_key_fields
        natural_key = {}
        for n, field in enumerate(fields):
            natural_key[field] = args[n]
        return self.get(**natural_key)


class User(AbstractUser):
    email = models.EmailField('email address', blank=True, unique=True)
    avatar = ProcessedImageField(
        null=True, blank=True,
        upload_to='account/profile_pictures/%Y/%m',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 70}
    )
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    locked = models.BooleanField('Lock the account', default=False)
    force_password_change = models.BooleanField('Prompt user to change password upon first login', default=False)

    # address = models.CharField(null=True, blank=True, max_length=100)
    # address2 = models.CharField(null=True, blank=True, max_length=40)
    # city = models.CharField(null=True, blank=True, max_length=20)
    # state = models.CharField(null=True, blank=True, max_length=2, choices=settings.STATES)
    # zip_code = models.CharField(null=True, blank=True, max_length=5)
    # BIRTH_YEAR_CHOICES = [ str(i) for i in range(datetime.date.today().year-70, datetime.date.today().year-7) ]
    # date_of_birth = models.DateField(null=True, blank=True)
    # email_subscription = models.NullBooleanField(default=None, choices=settings.EMAIL_SUBSCRIPTIONS)

    natural_key_fields = ['email']
    objects = UserManager()

    def __str__(self):
        """Prints for debugging purposes"""
        return self.get_full_name()

    @classmethod
    def create(cls, username=None, first_name=None, last_name=None):
        # if username is None:
        #     username = f'{first_name} {last_name}'
        user = cls()
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user

    def natural_key(self) -> Tuple[Any]:
        natural_key_fields = self.natural_key_fields
        natural_key_values = []
        for field in natural_key_fields:
            value = getattr(self, field, None)
            if not value:
                raise AttributeError(f'Model has no `{field}` attribute.')
            natural_key_values.append(value)
        return tuple(value for value in natural_key_values)

    def lock(self):
        self.locked = True
        self.save()

    def unlock(self):
        self.locked = False
        self.save()
