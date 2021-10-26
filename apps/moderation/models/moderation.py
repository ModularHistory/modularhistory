from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import ModerationStatus
from core.environment import IS_PROD
from core.utils.email import send_mass_html_mail
from core.utils.html import soupify

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
    reason = models.TextField(
        blank=True,
        null=True,
        help_text='The reason for the moderation verdict (approval or rejection)',
    )
    date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text='The date of the moderation',
    )

    # Boolean reflecting whether the moderation verdict is stale. This should be `False`
    # for a newly added moderation, but if a change is updated (i.e., if additional changes
    # are made), it should be set to `True` (so that the extant moderation becomes stale and
    # the change must be moderated again). A single moderator has only one non-stale
    # moderation at a time. NOTE: This field is used to avoid counting stale approvals
    # when determining whether a change has received the required number of approvals.
    stale = models.BooleanField(default=False)

    objects = ModerationManager()

    def __str__(self) -> str:
        return f'Verdict: {self.verdict} (moderation of {self.change} by {self.moderator})'

    @property
    def is_approval(self) -> bool:
        return self.verdict == ModerationStatus.APPROVED

    @property
    def is_rejection(self) -> bool:
        return self.verdict == ModerationStatus.REJECTED

    def notify_users(self):
        """Notify users of the moderation."""
        # TODO: ensure the notification is only sent once per moderation
        change: 'Change' = self.change
        moderator: Optional['User'] = self.moderator
        contributors: 'QuerySet[User]' = change.contributors.all()
        moderators: 'QuerySet[User]' = change.moderators.all()
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#union
        users = contributors.union(moderators)
        site = Site.objects.get_current()
        protocol = 'https' if IS_PROD else 'http'
        ctx = {
            'moderation': self,
            'moderator': moderator,
            'change': change,
            'content_object': change.content_object,
            'content_type': change.content_type,
            'site': site,
            'protocol': protocol,
        }
        passive_verb = (
            self.ModerationOutcome(self.verdict).label.lower()
            if self.verdict != ModerationStatus.PENDING
            else 'reviewed'
        )
        subject = f'Change was {passive_verb}'
        if moderator:
            subject = f'{subject} by {moderator.handle}'
        message_body_html = render_to_string(
            'moderation/moderation_notification_body.html', ctx
        )
        message_body_text = soupify(message_body_html).get_text()
        send_mass_html_mail(
            tuple(
                (
                    subject,
                    message_body_text,
                    message_body_html,
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
    """Proxy model for moderations with a verdict of APPROVED."""

    objects = ApprovalManager()

    class Meta:
        proxy = True


class RejectionManager(ModerationManager):
    def get_queryset(self) -> 'QuerySet[Rejection]':
        return super().get_queryset().filter(verdict=ModerationStatus.REJECTED)


class Rejection(Moderation):
    """Proxy model for moderations with a verdict of REJECTED."""

    objects = RejectionManager()

    class Meta:
        proxy = True
