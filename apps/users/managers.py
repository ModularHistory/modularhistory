from typing import TYPE_CHECKING

from django.db import models

from apps.users.constants import MAX_EMAIL_ADDRESSES

if TYPE_CHECKING:
    from apps.users.models import EmailAddress


class EmailAddressManager(models.Manager):
    """Manager for email addresses associated with users."""

    model: models.Model

    def can_add_email(self, user):
        ret = True
        if MAX_EMAIL_ADDRESSES:
            count = self.filter(user=user).count()
            ret = count < MAX_EMAIL_ADDRESSES
        return ret

    def add_email(self, request, user, email, confirm=False):
        email_address, created = self.get_or_create(
            user=user, email__iexact=email, defaults={'email': email}
        )
        if created and confirm:
            email_address.send_confirmation(request)
        return email_address

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None

    def get_users_for(self, email):
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in self.filter(verified=True, email__iexact=email)]

    def fill_cache_for_user(self, user, addresses):
        """
        In a multi-db setup, inserting records and re-reading them later
        on may result in not being able to find newly inserted
        records. Therefore, we maintain a cache for the user so that
        we can avoid database access when we need to re-read..
        """
        user._emailaddress_cache = addresses

    def get_for_user(self, user, email):
        cache_key = '_emailaddress_cache'
        addresses = getattr(user, cache_key, None)
        if addresses is None:
            email_address: 'EmailAddress' = self.get(user=user, email__iexact=email)
            # To avoid additional lookups when e.g.
            # EmailAddress.set_as_primary() starts touching self.user
            email_address.user = user
            return email_address
        else:
            for email_address in addresses:
                if email_address.email.lower() == email.lower():
                    return email_address
            raise self.model.DoesNotExist()
