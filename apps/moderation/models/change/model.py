import logging
from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from apps.moderation.constants import DraftState, ModerationStatus
from apps.moderation.fields import SerializedObjectField
from apps.moderation.models.changeset.model import AbstractChange
from apps.moderation.models.moderation import Moderation
from apps.moderation.tasks import handle_approval

from .manager import ChangeManager

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from apps.moderation.models.change import Change
    from apps.moderation.models.moderated_model import ModeratedModel
    from apps.users.models import User


class Change(AbstractChange):
    """
    A modification of a moderated model instance.

    A `Change` instance moves through the moderation statuses defined in `AbstractChange`,
    beginning with "pending" and then transitioning to "rejected" or "approved" depending
    on the verdict of moderators. If a change is approved, it will be applied to the
    moderated model instance that it references, at which point its status will finally be
    transitioned to "merged".
    """

    moderations: 'QuerySet[Moderation]'

    # Changes can stand alone or be included in `ChangeSet` instances.
    set = models.ForeignKey(
        to='moderation.ChangeSet',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Changes to m2m relationships require their own `Change` instances but can be
    # explicitly connected to their originating change through the `parent` field.
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='dependent_changes',
        null=True,
        blank=True,
    )

    # Django's content types framework is used to store references to moderated model
    # instances, which can belong to various models.
    # https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
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
        related_name='changes_contributed_to',
        through='moderation.ContentContribution',
    )
    moderators = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        related_name='changes_moderated',
        through='moderation.Moderation',
        blank=True,
    )

    # `merged_date` must be set automatically when change is applied to the moderated
    # model instance and the moderation status is updated from "approved" to "merged".
    merged_date = models.DateTimeField(null=True, blank=True, editable=False)

    objects = ChangeManager()

    def __str__(self) -> str:
        return f'Change affecting {self.content_object}'

    @property
    def is_approved(self) -> bool:
        """Return a boolean reflecting whether the change is approved."""
        return self.moderation_status == ModerationStatus.APPROVED

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
        if self.is_approved:
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

    def approve(
        self,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
    ) -> Moderation:
        """Add an approval."""
        approval = self.moderate(
            verdict=ModerationStatus.APPROVED,
            moderator=moderator,
            reason=reason,
        )
        handle_approval.delay(approval.pk)
        return approval

    def moderate(
        self,
        verdict: int,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
    ) -> Moderation:
        """Moderate the change."""
        if verdict not in self._ModerationStatus.values:
            raise ValueError(f'Verdict value must be one of {self._ModerationStatus.values}.')
        moderation: Moderation = Moderation.objects.create(
            moderator=moderator,
            change=self,
            verdict=verdict,
            reason=reason,
        )
        return moderation

    def reject(
        self,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
    ) -> Moderation:
        """Reject the change."""
        moderation: Moderation = self.moderate(
            verdict=ModerationStatus.REJECTED,
            moderator=moderator,
            reason=reason,
        )
        self.moderation_status = ModerationStatus.REJECTED
        self.save()
        return moderation
