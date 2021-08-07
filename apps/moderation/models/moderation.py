from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import ModerationStatus


class ModerationManager(models.Manager):
    """Manager for moderations."""


class Moderation(models.Model):
    """A moderation of a change."""

    class ModerationOutcome(models.IntegerChoices):
        """Possible moderation outcomes."""

        REJECTED = ModerationStatus.REJECTED, _('Rejected')
        PENDING = ModerationStatus.PENDING, _('Pending')
        APPROVED = ModerationStatus.APPROVED, _('Approved')

    moderator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name='moderations',
    )
    change = models.ForeignKey(
        to='moderation.Change',
        editable=False,
        on_delete=models.CASCADE,
        related_name='moderations',
    )
    verdict = models.PositiveSmallIntegerField(choices=ModerationOutcome.choices)
    reason = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, editable=False)

    objects = ModerationManager()

    def __str__(self) -> str:
        return f'Verdict: {self.verdict} (moderation of {self.change} by {self.moderator})'

    def retract(self):
        """Retract the moderation."""
        self.delete()


class ApprovalManager(ModerationManager):
    def get_queryset(self) -> QuerySet['Approval']:
        return super().get_queryset().filter(verdict=ModerationStatus.APPROVED)


class Approval(Moderation):
    objects = ApprovalManager()

    class Meta:
        proxy = True


class RejectionManager(ModerationManager):
    def get_queryset(self) -> QuerySet['Rejection']:
        return super().get_queryset().filter(verdict=ModerationStatus.REJECTED)


class Rejection(Moderation):
    objects = RejectionManager()

    class Meta:
        proxy = True
