import datetime
from typing import TYPE_CHECKING, Optional, Type

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import DraftState as _DraftState
from apps.moderation.constants import ModerationStatus as _ModerationStatus
from apps.moderation.diff import get_changes_between_models
from apps.moderation.models.change.model import ContentContribution
from apps.moderation.models.moderation import Moderation
from apps.moderation.signals import post_moderation, pre_moderation

from .manager import ChangeSetManager

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from django.db.models.query import QuerySet

    from apps.moderation.models.change import Change
    from apps.moderation.models.moderated_model import ModeratedModel
    from apps.users.models import User


class AbstractChange(models.Model):
    """Base model for the `Change` and `ChangeSet` models."""

    class Reason(models.IntegerChoices):
        """Reasons for a change."""

        ELABORATION = 0, _('Elaboration or expansion')
        CONTENT_CORRECTION = 1, _('Correction of content')
        GRAMMAR = 2, _('Correction of grammar or punctuation')

    class DraftState(models.IntegerChoices):
        """Draft states."""

        DRAFT = _DraftState.DRAFT, _('Draft')
        READY = _DraftState.READY, _('Ready for moderation')

    class ModerationStatus(models.IntegerChoices):
        """Moderation statuses."""

        REJECTED = _ModerationStatus.REJECTED, _('Rejected')
        PENDING = _ModerationStatus.PENDING, _('Pending')
        APPROVED = _ModerationStatus.APPROVED, _('Approved')
        MERGED = _ModerationStatus.MERGED, _('Merged')

    initiator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL,
        related_name='initiated_changesets',
    )
    reasons = ArrayField(
        base_field=models.PositiveSmallIntegerField(choices=Reason.choices),
        null=True,
        blank=True,
        help_text=_('Reason(s) for change(s)'),
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_('Description of changes made'),
    )
    draft_state = models.PositiveSmallIntegerField(
        choices=DraftState.choices,
        default=DraftState.DRAFT.value,
        editable=False,
    )
    moderation_status = models.PositiveSmallIntegerField(
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING.value,
        editable=False,
    )
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

    def approve(
        self,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
    ) -> Moderation:
        """Add an approval."""
        # self._send_signals_and_moderate(_ModerationStatus.APPROVED, by, reason)
        return self.moderate(
            verdict=_ModerationStatus.APPROVED,
            moderator=moderator,
            change=self,
            reason=reason,
        )

    def moderate(
        self,
        verdict: ModerationStatus,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
    ) -> Moderation:
        """Moderate the change."""
        return Moderation.objects.create(
            moderator=moderator,
            change=self,
            verdict=verdict,
            reason=reason,
        )

    def reject(
        self,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
    ) -> Moderation:
        """Reject the change."""
        # self._send_signals_and_moderate(_ModerationStatus.REJECTED, by, reason)
        moderation: Moderation = self.moderate(
            verdict=_ModerationStatus.REJECTED,
            moderator=moderator,
            reason=reason,
        )
        self.moderation_status = _ModerationStatus.REJECTED
        self.save()
        return moderation


class ChangeSet(AbstractChange):
    """A set of changes to one or more moderated model instances."""

    changes: 'RelatedManager[Change]'

    objects = ChangeSetManager()

    class Meta:
        verbose_name = _('change set')
        verbose_name_plural = _('change sets')
        ordering = ['moderation_status', 'created_date']

    def __str__(self):
        return f'Changeset #{self.pk}, initiated {self.created_date} by {self.initiator}'

    def save(self, *args, **kwargs):
        if self.instance:
            self.changed_object = self.instance
        super().save(*args, **kwargs)

    @property
    def change_ids(self) -> list[int]:
        return self.changes.all().values_list('id', flat=True)

    @property
    def contributions(self) -> 'QuerySet[ContentContribution]':
        return ContentContribution.objects.filter(change_id__in=self.change_ids)

    @property
    def contributors(self) -> 'QuerySet[User]':
        return get_user_model().objects.filter(
            content_contributions__change_id__in=self.change_ids
        )

    def _send_signals_and_moderate(self, new_status, by, reason):
        pre_moderation.send(
            sender=self.changed_object.__class__,
            instance=self.changed_object,
            status=new_status,
        )

        self._moderate(new_status, by, reason)

        post_moderation.send(
            sender=self.content_type.model_class(),
            instance=self.content_object,
            status=new_status,
        )

    def _moderate(self, new_status, moderator, reason):
        # See register.py pre_save_handler() for the case where the model is
        # reset to its old values, and the new values are stored in the
        # Moderation. In such cases, on approval, we should restore the
        # changes to the base object by saving the one attached to the
        # Moderation.

        if (
            self.moderation_status == _ModerationStatus.PENDING
            and new_status == _ModerationStatus.APPROVED
        ):
            base_object = self.changed_object
            base_object_force_save = True
        else:
            # The model in the database contains the most recent data already,
            # or we're not ready to approve the changes stored in
            # Moderation.
            obj_class = self.changed_object.__class__
            pk = self.changed_object.pk
            base_object = obj_class._default_unmoderated_manager.get(pk=pk)
            base_object_force_save = False

        if new_status == _ModerationStatus.APPROVED:
            # This version is now approved, and will be reverted to if
            # future changes are rejected by a moderator.
            self.draft_state = _DraftState.READY

        self.moderation_status = new_status
        self.on = datetime.datetime.now()
        self.moderator = moderator
        self.reason = reason
        self.save()

        visibility_column = 'verified'
        if visibility_column:
            old_visible = getattr(base_object, visibility_column)
            if new_status == _ModerationStatus.APPROVED:
                new_visible = True
            else:
                new_visible = False
            if new_visible != old_visible:
                setattr(base_object, visibility_column, new_visible)
                base_object_force_save = True

        if base_object_force_save:
            # avoid triggering pre/post_save_handler
            with transaction.atomic(using=None, savepoint=False):
                base_object.save_base(raw=True)
                # The _save_parents call is required for models with an
                # inherited visibility_column.
                base_object._save_parents(base_object.__class__, None, None)

        if self.initiator:
            self.moderator.inform_user(self.content_object, self.initiator)

    def has_object_been_changed(self, original_obj, only_excluded=False):
        excludes = includes = []
        if only_excluded:
            includes = self.moderator.fields_exclude
        else:
            excludes = self.moderator.fields_exclude

        changes = get_changes_between_models(
            original_obj, self.changed_object, excludes, includes
        )

        for change in changes:
            left_change, right_change = changes[change].change
            if left_change != right_change:
                return True

        return False
