from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
# from history.models import Model
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class User(AbstractUser):
    # address = models.CharField(null=True, blank=True, max_length=100)
    # address2 = models.CharField(null=True, blank=True, max_length=40)
    # city = models.CharField(null=True, blank=True, max_length=20)
    # state = models.CharField(null=True, blank=True, max_length=2, choices=settings.STATES)
    # zip_code = models.CharField(null=True, blank=True, max_length=5)
    # BIRTH_YEAR_CHOICES = [ str(i) for i in range(datetime.date.today().year-70, datetime.date.today().year-7) ]
    # date_of_birth = models.DateField(null=True, blank=True)
    avatar = ProcessedImageField(
        null=True, blank=True,
        upload_to='account/profile_pictures/%Y/%m',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 70}
    )
    # email_subscription = models.NullBooleanField(default=None, choices=settings.EMAIL_SUBSCRIPTIONS)
    force_password_change = models.BooleanField('Prompt user to change password upon first login', default=False)
    locked = models.BooleanField('Lock the account', default=False)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        """Prints for debugging purposes"""
        return self.get_full_name()

    @classmethod
    def create(cls, username=None, first_name=None, last_name=None, gender=None):
        # if username is None:
        #     username = f'{first_name} {last_name}'
        user = cls()
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        print(f'>>> Created user: {user}')
        return user

    def lock(self):
        self.locked = True
        self.save()

    def unlock(self):
        self.locked = False
        self.save()
