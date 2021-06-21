from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.interactions.models import ContentInteraction
from core.models.model import Model


class VerifiableModel(Model):
    """An item that can, hopefully, be researched and verified."""

    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    verifications = GenericRelation('verifications.Verification')

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for VerifiableModel."""

        abstract = True


class Verification(ContentInteraction):
    """A verification of the veracity of a verifiable model instance's content."""

    verifier = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verifications',
        verbose_name=_('verifier'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    verified_item = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    def __str__(self) -> str:
        """Return the string representation of the verification."""
        return f'Verification: {self.verifier}, {self.verified_item}'
