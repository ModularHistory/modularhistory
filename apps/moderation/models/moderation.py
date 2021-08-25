from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mass_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import ModerationStatus

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from apps.moderation.models.change import Change
    from apps.users.models import User


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

    def notify_users(self):
        """Notify users of the moderation."""
        # TODO: ensure the notification is only sent once per moderation
        change: 'Change' = self.change
        contributors: 'QuerySet[User]' = change.contributors.all()
        moderators: 'QuerySet[User]' = change.moderators.all()
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#union
        users = contributors.union(moderators)
        site = Site.objects.get_current()
        ctx = {
            'moderation': self,
            'content_object': change.content_object,
            'site': site,
            'content_type': change.content_type,
        }
        passive_verb = (
            self.ModerationOutcome(self.verdict).label.lower()
            if self.verdict != ModerationStatus.PENDING
            else 'reviewed'
        )
        subject = f'Change was {passive_verb}'
        message_body = render_to_string(
            'moderation/moderation_notification_body.txt',
            ctx.update({'user': change.initiator}),
        )
        # https://docs.djangoproject.com/en/dev/topics/email/#send-mass-mail
        send_mass_mail(
            tuple(
                (
                    subject,
                    message_body,
                    f'do.not.reply@{site.domain}',  # from email
                    [user.email],  # recipient list
                )
                for user in users
            ),
            fail_silently=True,
        )

    def retract(self):
        """Retract the moderation."""
        self.delete()


class ApprovalManager(ModerationManager):
    def get_queryset(self) -> 'QuerySet[Approval]':
        return super().get_queryset().filter(verdict=ModerationStatus.APPROVED)


class Approval(Moderation):
    objects = ApprovalManager()

    class Meta:
        proxy = True


class RejectionManager(ModerationManager):
    def get_queryset(self) -> 'QuerySet[Rejection]':
        return super().get_queryset().filter(verdict=ModerationStatus.REJECTED)


class Rejection(Moderation):
    objects = RejectionManager()

    class Meta:
        proxy = True
