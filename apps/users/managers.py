from typing import TYPE_CHECKING, Optional

from django.db import models

from apps.users.constants import MAX_EMAIL_ADDRESSES

if TYPE_CHECKING:
    from apps.users.models import EmailAddress


class EmailAddressManager(models.Manager):
    """Manager for email addresses associated with users."""

    model: models.Model

    def can_add_email(self, user):
        return self.filter(user=user).count() < MAX_EMAIL_ADDRESSES

    def add_email(self, request, user, email, confirm=False):
        email_address: 'EmailAddress'
        email_address, created = self.get_or_create(
            user=user, email__iexact=email, defaults={'email': email}
        )
        if created and confirm:
            email_address.send_confirmation(request)
        return email_address

    def get_primary(self, user) -> Optional['EmailAddress']:
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None
