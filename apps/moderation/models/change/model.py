from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.moderation.fields import SerializedObjectField
from apps.moderation.models.changeset.model import AbstractChange

from .manager import ChangeManager

if TYPE_CHECKING:
    pass


class ContentContribution(models.Model):
    """A contribution to a change."""

    contributor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name='content_contributions',
    )
    change = models.ForeignKey(
        to='moderation.Change',
        editable=False,
        on_delete=models.CASCADE,
        related_name='contributions',
    )

    def __str__(self) -> str:
        return f'Contribution by {self.contributor} to {self.change}'


class Change(AbstractChange):
    """A modification of a moderated model instance."""

    set = models.ForeignKey(to='moderation.ChangeSet', on_delete=models.CASCADE)
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
        through=ContentContribution,
    )
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)
    draft_state = models.PositiveSmallIntegerField(
        choices=AbstractChange.DraftState.choices,
        default=AbstractChange.DraftState.DRAFT.value,
        editable=False,
    )
    moderation_status = models.PositiveSmallIntegerField(
        choices=AbstractChange.ModerationStatus.choices,
        default=AbstractChange.ModerationStatus.PENDING.value,
        editable=False,
    )

    objects = ChangeManager()

    def __str__(self) -> str:
        return f'Change #{self.pk}, affecting {self.content_object}'
