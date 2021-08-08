from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.moderation.constants import ModerationStatus
from apps.moderation.fields import SerializedObjectField
from apps.moderation.models.changeset.model import AbstractChange

from .manager import ChangeManager

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import ModeratedModel


class Change(AbstractChange):
    """A modification of a moderated model instance."""

    set = models.ForeignKey(
        to='moderation.ChangeSet',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    content_type = models.ForeignKey(
        to=ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        editable=False,
    )
    content_type.content_type_filter = True
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )
    # `content_object` holds the existing (unmodified) instance.
    content_object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id',
    )
    # `changed_object` holds the modified instance, serialized.
    changed_object = SerializedObjectField(editable=False)
    contributors = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        through='moderation.ContentContribution',
    )

    objects = ChangeManager()

    def __str__(self) -> str:
        return f'Change #{self.pk}, affecting {self.content_object}'

    @property
    def unchanged_object(self) -> 'ModeratedModel':
        # TODO: account for possibility the change has been approved but not yet merged
        if self.moderation_status == ModerationStatus.APPROVED:
            prior_state = Change.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                moderation_status=ModerationStatus.APPROVED,
            )
            return self.content_object
        return self.content_object
