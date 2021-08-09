import datetime
from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import DraftState as _DraftState
from apps.moderation.constants import ModerationStatus as _ModerationStatus
from apps.moderation.diff import get_changes_between_models
from apps.moderation.models.contribution import ContentContribution
from apps.moderation.models.moderation import Moderation
from apps.moderation.tasks import handle_approval

from .manager import ChangeSetManager

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from django.db.models.query import QuerySet

    from apps.moderation.models.change import Change
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
        related_name='initiated_%(class)ss',
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
        default=_DraftState.DRAFT,
        editable=False,
    )
    moderation_status = models.PositiveSmallIntegerField(
        choices=ModerationStatus.choices,
        default=_ModerationStatus.PENDING,
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
        approval = self.moderate(
            verdict=_ModerationStatus.APPROVED,
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
        if verdict not in self.ModerationStatus.values:
            raise ValueError(f'Verdict value must be one of {self.ModerationStatus.values}.')
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

    def __str__(self) -> str:
        return f'Changeset #{self.pk}, initiated {self.created_date} by {self.initiator}'

    @property
    def change_ids(self) -> list[int]:
        """Return a list of the ids of the changes in the change set."""
        return self.changes.all().values_list('id', flat=True)

    @property
    def contributions(self) -> 'QuerySet[ContentContribution]':
        return ContentContribution.objects.filter(change_id__in=self.change_ids)

    @property
    def contributors(self) -> 'QuerySet[User]':
        return get_user_model().objects.filter(
            content_contributions__change_id__in=self.change_ids
        )

    def _moderate(self, verdict: int, moderator: Optional['User'], reason: Optional[str]):
        # The model in the database contains the most recent data already,
        # or we're not ready to approve the changes stored in
        # Moderation.
        obj_class = self.changed_object.__class__
        pk = self.changed_object.pk
        base_object = obj_class._default_unmoderated_manager.get(pk=pk)
        base_object_force_save = False

        if verdict == _ModerationStatus.APPROVED:
            # This version is now approved, and will be reverted to if
            # future changes are rejected by a moderator.
            self.draft_state = _DraftState.READY

        self.moderation_status = verdict
        self.on = datetime.datetime.now()
        self.moderator = moderator
        self.reason = reason
        self.save()

        visibility_column = 'verified'
        if visibility_column:
            old_visible = getattr(base_object, visibility_column)
            if verdict == _ModerationStatus.APPROVED:
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

        # TODO: celery task
        # post_moderation.send(
        #     sender=self.content_type.model_class(),
        #     instance=self.content_object,
        #     status=verdict,
        # )

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
