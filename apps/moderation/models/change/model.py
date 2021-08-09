import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from apps.moderation.constants import DraftState, ModerationStatus
from apps.moderation.fields import SerializedObjectField
from apps.moderation.models.changeset.model import AbstractChange

from .manager import ChangeManager

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import ModeratedModel


class Change(AbstractChange):
    """
    A modification of a moderated model instance.

    A `Change` instance moves through the moderation statuses defined in `AbstractChange`,
    beginning with "pending" and then transitioning to "rejected" or "approved" depending
    on the verdict of moderators. If a change is approved, it will be applied to the
    moderated model instance that it references, at which point its status will finally be
    transitioned to "merged".
    """

    # Changes can stand alone or be included in `ChangeSet` instances.
    set = models.ForeignKey(
        to='moderation.ChangeSet',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Django's content types framework is used to store references to moderated model
    # instances, which can belong to various models.
    # https://docs.djangoproject.com/en/3.2/ref/contrib/contenttypes/
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )
    content_type.content_type_filter = True
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )
    content_object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id',
    )

    # `changed_object` holds the modified model instance. In the database, it is a JSON blob
    # (resulting from serialization), but in our Python application, it is the model instance
    # with changes applied. As such, `changed_object` can be compared with the
    # `unchanged_object` property to get the change diff.
    changed_object = SerializedObjectField(editable=False)

    contributors = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        through='moderation.ContentContribution',
    )

    # `merged_date` must be set automatically when change is applied to the moderated
    # model instance and the moderation status is updated from "approved" to "merged".
    merged_date = models.DateTimeField(null=True, blank=True, editable=False)

    objects = ChangeManager()

    def __str__(self) -> str:
        return f'Change #{self.pk}, affecting {self.content_object}'

    @property
    def unchanged_object(self) -> 'ModeratedModel':
        """
        Return the object prior to application of the change.

        If the change has not yet been saved to the moderated model instance,
        then the `unchanged_object` is simply the moderated model instance.

        If the change has already been applied, regardless of whether additional
        changes have been applied since the time this change was applied, the
        value of `unchanged_object` is the `changed_object` value of the
        change that immediately preceded this one.
        """
        if self.merged_date:
            prior_change: Change = Change.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                moderation_status=ModerationStatus.MERGED,
                merged_date__lt=self.merged_date,
            ).order_by('-merged_date')[0]
            return prior_change.changed_object
        return self.content_object

    def apply(self) -> bool:
        """
        Apply the change to the referenced model instance.

        Return a boolean reflecting whether the change was applied successfully.
        """
        if self.moderation_status == ModerationStatus.APPROVED:
            # Draft state should already be set to "ready".
            self.draft_state = DraftState.READY
            try:
                with transaction.atomic():
                    model_instance: 'ModeratedModel' = self.changed_object
                    model_instance.save()
            except Exception as err:
                logging.error(err)
                return False
            return True
        logging.info(f'Ignored request to apply unapproved change: {self}')
        return False
