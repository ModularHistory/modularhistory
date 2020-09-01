from typing import Optional

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.db.models import QuerySet
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from social_django.models import UserSocialAuth

from history.fields.file_field import upload_to


class UserManager(BaseUserManager):
    pass


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    avatar = ProcessedImageField(
        null=True, blank=True,
        upload_to=upload_to('account/avatars'),
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

    social_auth: 'QuerySet[UserSocialAuth]'
    objects: UserManager = UserManager()

    def __str__(self):
        return self.get_full_name()

    @property
    def social_auths(self) -> 'QuerySet[UserSocialAuth]':
        """Wrapper for the reverse attribute of the UserSocialAuth–User relation."""
        return self.social_auth

    def lock(self):
        self.locked = True
        self.save()

    def unlock(self):
        self.locked = False
        self.save()

