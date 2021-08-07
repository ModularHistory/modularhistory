import datetime
from typing import TYPE_CHECKING, Optional, Type

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import DraftState as _DraftState
from apps.moderation.constants import ModerationStatus as _ModerationStatus
from apps.moderation.diff import get_changes_between_models
from apps.moderation.models.moderation import Moderation
from apps.moderation.signals import post_moderation, pre_moderation

from .manager import ChangeSetManager

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

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
        return Moderation.objects.create(
            moderator=moderator,
            change=self,
            verdict=_ModerationStatus.APPROVED,
            reason=reason,
        )

    def reject(
        self,
        moderator: Optional['User'] = None,
        reason: Optional[str] = None,
    ) -> Moderation:
        """Reject the change."""
        # self._send_signals_and_moderate(_ModerationStatus.REJECTED, by, reason)
        moderation: Moderation = Moderation.objects.create(
            moderator=moderator,
            change=self,
            verdict=_ModerationStatus.REJECTED,
            reason=reason,
        )
        self.moderation_status = _ModerationStatus.REJECTED
        self.save()
        return moderation


class ChangeSet(AbstractChange):
    """A set of changes to one or more moderated model instances."""

    changes: 'RelatedManager[Change]'
    initiator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL,
        related_name='initiated_changesets',
    )

    objects = ChangeSetManager()

    def __str__(self):
        return f'Changeset #{self.pk}, initiated {self.created_date} by {self.initiator}'

    def save(self, *args, **kwargs):
        if self.instance:
            self.changed_object = self.instance
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('modification')
        verbose_name_plural = _('modifications')
        ordering = ['moderation_status', 'created_date']

    def automoderate(self, user=None) -> AbstractChange.ModerationStatus:
        """Auto-moderate the modification based on the user; return the moderation status."""
        if user is None:
            user = self.initiator
        else:
            self.initiator = user
            # No need to save here, both reject() and approve() will save us.
            # Just save below if the moderation result is PENDING.
        changed_object = self.changed_object
        status, reason = self._get_moderation_status_and_reason(changed_object, user)
        if status == _ModerationStatus.REJECTED:
            self.reject(by=self.by, reason=reason)
        elif status == _ModerationStatus.APPROVED:
            self.approve(by=self.by, reason=reason)
        else:  # PENDING
            self.save()

        return status

    def _get_moderation_status_and_reason(self, obj, user):
        """
        Returns tuple of moderation status and reason for auto moderation
        """
        reason = self.moderator.is_auto_reject(obj, user)
        if reason:
            return _ModerationStatus.REJECTED, reason
        else:
            reason = self.moderator.is_auto_approve(obj, user)
            if reason:
                return _ModerationStatus.APPROVED, reason
        return _ModerationStatus.PENDING, None

    def get_absolute_url(self):
        if hasattr(self.changed_object, 'get_absolute_url'):
            return self.changed_object.get_absolute_url()
        return None

    def get_admin_moderate_url(self):
        return f'/admin/moderation/moderatedobject/{self.pk}/change/'

    @property
    def moderator(self):
        model_class: Type['ModeratedModel'] = self.content_type.model_class()
        return model_class.Moderator(model_class)  # TODO: singleton?

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
