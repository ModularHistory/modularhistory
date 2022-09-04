import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import N_REQUIRED_APPROVALS, DraftState, ModerationStatus
from apps.moderation.models.contribution import ContentContribution

from .manager import ChangeSetManager

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from django.db.models.query import QuerySet

    from apps.moderation.models.change import Change
    from apps.users.models import User


class AbstractChange(models.Model):
    """Base model for the `Change` and `ChangeSet` models."""

    n_required_approvals = N_REQUIRED_APPROVALS

    class Reason(models.IntegerChoices):
        """Reasons for a change."""

        ELABORATION = 0, _('Elaboration or expansion')
        CONTENT_CORRECTION = 1, _('Correction of content')
        GRAMMAR = 2, _('Correction of grammar or punctuation')

    class _DraftState(models.IntegerChoices):
        """Draft states."""

        DRAFT = DraftState.DRAFT, _('Draft')
        READY = DraftState.READY, _('Ready for moderation')

    class _ModerationStatus(models.IntegerChoices):
        """Moderation statuses."""

        REJECTED = ModerationStatus.REJECTED, _('Rejected')
        PENDING = ModerationStatus.PENDING, _('Pending')
        APPROVED = ModerationStatus.APPROVED, _('Approved')

    initiator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL,
        related_name='%(class)ss_initiated',
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
        choices=_DraftState.choices,
        default=_DraftState.DRAFT.value,  # type: ignore
        editable=False,
    )
    moderation_status = models.PositiveSmallIntegerField(
        choices=_ModerationStatus.choices,
        default=_ModerationStatus.PENDING.value,  # type: ignore
        editable=False,
    )
    n_remaining_approvals_required = models.PositiveSmallIntegerField(
        verbose_name=_('number of remaining approvals required'),
        blank=True,
        default=n_required_approvals,
        editable=False,
    )
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


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
        """Return a list of ids of changes in the change set."""
        return self.changes.all().values_list('id', flat=True)

    @property
    def contributions(self) -> 'QuerySet[ContentContribution]':
        """Return a queryset of contributions to changes in the change set."""
        return ContentContribution.objects.filter(change_id__in=self.change_ids)

    @property
    def contributors(self) -> 'QuerySet[User]':
        """Return a queryset of users who have contributed to changes in the change set."""
        return get_user_model().objects.filter(
            content_contributions__change_id__in=self.change_ids
        )

    def apply(self) -> bool:
        """Apply the change set to the referenced model instances."""
        if self.moderation_status == ModerationStatus.APPROVED:
            try:
                self.changes.all().apply()
            except Exception as err:
                logging.error(err)
                return False
            return True
        logging.info(f'Ignored request to apply unapproved changeset: {self}')
        return False
