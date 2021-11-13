import logging
from tempfile import NamedTemporaryFile
from typing import Optional
from urllib.parse import urlsplit
from urllib.request import urlopen

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.files import File
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db import models, transaction
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ugettext_lazy as _
from django_cryptography.fields import encrypt

from apps.users.constants import EMAIL_CONFIRMATION_EXPIRE_DAYS, SALT
from apps.users.managers import EmailAddressManager
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

    def save(self, *args, **kwargs):
        """Save the user data to the db."""
        if not self.handle:
            self.handle = handlify(self.get_handle_base())
        super().save(*args, **kwargs)

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


class EmailAddress(models.Model):
    """An email address associated with a user."""

    user = models.ForeignKey(
        to=User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='email_addresses',
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('e-mail address'),
    )
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    primary = models.BooleanField(verbose_name=_('primary'), default=False)

    objects: EmailAddressManager = EmailAddressManager()

    class Meta:
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        if not self.user.email_addresses.exclude(email=self.email).exists():
            self.primary = True
        super().save(*args, **kwargs)

    def set_as_primary(self):
        """Set the email address as its user's primary email address."""
        old_primary: Optional[EmailAddress] = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        user: User = self.user
        user.email = self.email
        user.save()

    def send_confirmation(self, request=None) -> 'EmailConfirmation':
        confirmation = EmailConfirmation(self)
        confirmation.send(request)
        return confirmation

    def change(self, request, new_email, confirm=True):
        """Change the email address and re-confirm if necessary."""
        with transaction.atomic():
            user: User = self.user
            user.email = new_email
            user.save()
            self.email = new_email
            self.verified = False
            self.save()
            if confirm:
                self.send_confirmation(request)


class EmailConfirmation:
    """An email address confirmation using an HMAC-based key."""

    def __init__(self, email_address: EmailAddress):
        self.email_address = email_address

    @property
    def key(self) -> str:
        return signing.dumps(obj=self.email_address.pk, salt=SALT)

    @classmethod
    def from_key(cls, key) -> Optional['EmailConfirmation']:
        try:
            max_age = 60 * 60 * 24 * EMAIL_CONFIRMATION_EXPIRE_DAYS
            pk = signing.loads(key, max_age=max_age, salt=SALT)
            return EmailConfirmation(EmailAddress.objects.get(pk=pk))
        except (
            signing.SignatureExpired,
            signing.BadSignature,
            EmailAddress.DoesNotExist,
        ):
            return None

    def confirm(self, request):
        email_address: EmailAddress = self.email_address
        if not email_address.verified:
            email_address.verified = True
            email_address.save()
        return email_address

    def send(self, request=None):
        site = get_current_site(request)
        user: User = self.email_address.user
        location = f'/users/email-confirmation/{self.key}'
        if request is None:
            bits = urlsplit(location)
            if not (bits.scheme and bits.netloc):
                activation_url = '{proto}://{domain}{url}'.format(
                    proto=settings.HTTP_PROTOCOL,
                    domain=settings.DOMAIN,
                    url=location,
                )
            else:
                activation_url = location
        else:
            activation_url = request.build_absolute_uri(location)
        # Only force the protocol if the default is set to HTTPS.
        protocol = settings.HTTP_PROTOCOL if settings.HTTP_PROTOCOL == 'https' else ''
        if protocol:
            activation_url = protocol + ':' + activation_url.partition(':')[2]
        context = {
            'user': user,
            'activation_url': activation_url,
            'site': site,
            'key': self.key,
        }
        email_template_prefix = 'users/email_confirmation'
        email = self.email_address.email
        to = [email] if isinstance(email, str) else email
        subject = render_to_string('{0}/subject.txt'.format(email_template_prefix), context)
        # Remove superfluous line breaks.
        subject = ' '.join(subject.splitlines()).strip()
        from_email = settings.DEFAULT_FROM_EMAIL
        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = '{0}/message.{1}'.format(email_template_prefix, ext)
                bodies[ext] = render_to_string(
                    template_name,
                    context,
                    request=request,
                ).strip()
            except TemplateDoesNotExist:
                if ext == 'txt' and not bodies:
                    # We need at least one body
                    raise
        if 'txt' in bodies:
            msg = EmailMultiAlternatives(subject, bodies['txt'], from_email, to)
            if 'html' in bodies:
                msg.attach_alternative(bodies['html'], 'text/html')
        else:
            msg = EmailMessage(subject, bodies['html'], from_email, to)
            msg.content_subtype = 'html'  # Main content is now text/html.
        msg.send()
