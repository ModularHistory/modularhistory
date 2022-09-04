import logging
from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import DraftState, ModerationStatus
from apps.moderation.fields import SerializedObjectField
from apps.moderation.models.changeset.model import AbstractChange
from apps.moderation.models.moderation import Moderation
from apps.moderation.tasks import handle_approval
from core.utils.sync import delay

from .manager import ChangeManager

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from apps.moderation.models.change.queryset import ChangeQuerySet
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
        related_name='constituent_changes',
        null=True,
        blank=True,
    )
    constituent_changes: 'ChangeQuerySet'  # from parent's `related_name`

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

    # Boolean reflecting whether the change needs to be rebased on a preceding change.
    requires_rebase = models.BooleanField(
        verbose_name=_('requires rebase'),
        editable=False,
        default=False,
    )

    # `merged_date` must be set automatically when change is applied to the moderated
    # model instance and the moderation status is updated from "approved" to "merged".
    merged_date = models.DateTimeField(null=True, blank=True, editable=False)

    objects = ChangeManager()

    def __str__(self) -> str:
        return f'Change affecting {self.content_object}'

    @property
    def is_approved(self) -> bool:
        """Return a boolean reflecting whether the change has been approved."""
        return self.moderation_status == ModerationStatus.APPROVED

    @property
    def unchanged_object(self) -> 'ModeratedModel':
        """
        Return the object prior to application of the change.

        If the change has already been applied, the value of `unchanged_object` is the
        `changed_object` value of the change that was applied immediately before this one.
        """
        if self.merged_date:
            previously_merged_change: Optional['Change'] = self.get_previously_merged_change()
            if previously_merged_change:
                return previously_merged_change.changed_object
        return self.content_object

    def get_initial_object_of_change(self) -> 'ModeratedModel':
        """
        Return the object against which this change was initially proposed.

        This can be used for rebasing the change (Change A) on another change (Change B)
        that was applied to the referenced model instance after Change A was initiated.

        Change A's initial object of change can be compared against the `changed_object`
        value of Change B. Note: Change B is probably the return value of
        `change_a.get_previously_merged_change()`.
        """
        prior_changes = self.__class__.objects.filter(merged_date__lt=self.created_date)
        if prior_changes.exists():
            prior_change: 'Change' = prior_changes.order_by('-merged_date')[0]
            return prior_change.changed_object
        # If there were no changes merged before this change was initiated, we will
        # assume that the initial object of change is the current content object.
        return self.content_object

    def get_n_remaining_approvals_required(self) -> int:
        """Return the number of remaining approvals required before the change is applied."""
        if self.is_approved:
            return 0
        n_required_approvals = self.n_required_approvals
        latest_moderations = self.moderations.order_by('-date')[:n_required_approvals]
        for moderation in latest_moderations:
            if moderation.verdict == ModerationStatus.APPROVED:
                n_required_approvals -= 1
            else:
                break
        return n_required_approvals

    def get_previously_merged_change(self) -> Optional['Change']:
        """
        Return the latest-merged change preceding this one, or None.

        If this change has not been merged:
            Return the most recently merged change.

        If this change has been merged:
            Return the change that was merged immediately before this one.

        If no changes, excluding this one, have been merged, return None.
        """
        previously_merged_change_kwargs = {
            'content_type': self.content_type,
            'object_id': self.object_id,
        }
        if self.merged_date:
            previously_merged_change_kwargs['merged_date__lt'] = self.merged_date
        else:
            previously_merged_change_kwargs['merged_date__isnull'] = False
        previously_merged_changes = Change.objects.filter(**previously_merged_change_kwargs)
        if previously_merged_changes.exists():
            previously_merged_change: Change = previously_merged_changes.order_by(
                '-merged_date'
            )[0]
            return previously_merged_change
        return None

    def apply(self) -> bool:
        """
        Apply the change to the referenced model instance.

        Return a boolean reflecting whether the change was applied successfully.
        """
        parent: Optional['Change'] = self.parent
        if self.requires_rebase:
            raise Exception(f'{self} cannot be applied; it requires rebasing.')
        elif parent and parent.requires_rebase:
            raise Exception(f'{self} cannot be applied; its parent change requires rebasing.')
        elif self.is_approved:
            # Draft state should already be set to "ready".
            self.draft_state = DraftState.READY
            try:
                with transaction.atomic():
                    model_instance: 'ModeratedModel' = self.changed_object
                    model_instance.save(moderate=False)
                    self.merged_date = timezone.now()
                    self.save()
            except Exception as err:
                logging.error(err)
                return False
            # Update other changes that require rebasing on this one.
            self.__class__.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                merged_date__isnull=True,
            ).exclude(pk=self.pk).update(requires_rebase=True)
            return True
        logging.error(f'Ignored request to apply unapproved change: {self}')
        return False

    def approve(
        self,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
        force: bool = False,
    ) -> Moderation:
        """
        Add an approval to the change.

        By default, this does not change the moderation status of the change
        until the total number of approvals reaches the required number of
        approvals (`n_required_approvals`). However, if the moderator is a
        superuser and `force=True` is specified, the moderation status is
        immediately updated to APPROVED, and the change is applied.
        """
        # If the moderator has already approved the change (in its current state),
        # don't add another approval; instead, log an error and return the extant approval.
        # This prevents a single moderator from approving a change multiple times and
        # circumventing `n_required_approvals`. NOTE: A moderator can re-approve a change
        # after it is updated; we exclude stale moderations from this check.
        extant_approvals = self.moderations.filter(
            moderator=moderator,
            verdict=ModerationStatus.APPROVED,
            stale=False,
        )
        if extant_approvals.exists():
            if force:
                # Still allow force-approval, but invalidate prior (presumably
                # non-forced) approvals by the moderator so that there's only one
                # effective approval by the moderator.
                extant_approvals.update(stale=True)
            else:
                logging.error('Attempted to duplicate an approval.')
                return extant_approvals.first()
        approval = self.moderate(
            verdict=ModerationStatus.APPROVED,
            moderator=moderator,
            reason=reason,
            force=force,
        )
        self.constituent_changes.all().approve(moderator=moderator, reason=reason)
        delay(handle_approval, approval.pk)
        return approval

    def moderate(
        self,
        verdict: int,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
        force: bool = False,
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
        if force:
            if moderator and moderator.is_superuser:
                self.moderation_status = verdict
                self.save()
            else:
                logging.error(
                    f'Cannot process force-approval by non-superuser moderator {moderator}.'
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
        self.n_remaining_approvals_required = self.n_required_approvals
        self.save()
        return moderation

    def update(self, changed_object: 'ModeratedModel') -> bool:
        """
        Update the change's changed object and reset the number of required approvals.

        Returns a boolean reflecting whether the object was actually changed.
        """
        if self.changed_object == changed_object:
            return False
        # Update the changed object.
        self.changed_object = changed_object
        # Reset the number of remaining approvals required.
        self.n_remaining_approvals_required = self.n_required_approvals
        # Invalidate extant approvals by setting stale=True.
        self.moderations.filter(stale=False, verdict=ModerationStatus.APPROVED).update(
            stale=True
        )
        # Update the change status to "pending".
        self.moderation_status = ModerationStatus.PENDING
        self.save()
        return True
