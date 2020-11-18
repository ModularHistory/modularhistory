from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from modularhistory.models.model import Model


class VerifiableModel(Model):
    """An item that can, hopefully, be researched and verified."""

    verified = models.BooleanField(_('verified'), default=False)

    class Meta:
        """
        Meta options for VerifiableModel.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        abstract = True


class Verification(Model):
    """A verification of the veracity of a verifiable model instance's content."""

    verifier = models.ForeignKey(
        'account.User', verbose_name=_('verifier'), on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    verified_item = GenericForeignKey('content_type', 'object_id')

    def __str__(self) -> str:
        """Return the string representation of the verification."""
        return f'Verification: {self.verifier}, {self.verified_item}'
