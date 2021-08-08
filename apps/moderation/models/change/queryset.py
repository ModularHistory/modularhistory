from datetime import datetime
from typing import TYPE_CHECKING, Optional, Type

from django.db.models.query import QuerySet

from apps.moderation.constants import DraftState, ModerationStatus
from apps.moderation.signals import post_moderation

if TYPE_CHECKING:
    from apps.moderation.models.change import Change
    from apps.users.models import User


class ChangeQuerySet(QuerySet):

    model: Type['Change']

    def approve(self, moderator: Optional['User'], reason: Optional[str] = None):
        """Approve the changes."""
        self._moderate(
            verdict=ModerationStatus.APPROVED,
            moderator=moderator,
            reason=reason,
        )

    def reject(self, moderator: Optional['User'], reason: Optional[str] = None):
        """Reject the changes."""
        self._moderate(
            verdict=ModerationStatus.REJECTED,
            moderator=moderator,
            reason=reason,
        )

    def _moderate(
        self,
        verdict: int,
        moderator: Optional['User'],
        reason: Optional[str] = None,
    ):
        """Update the moderation status of the changes."""
        kwargs = {
            'moderation_status': verdict,
            'date': datetime.now(),
            'moderator': moderator,
            'reason': reason,
        }
        if verdict == ModerationStatus.APPROVED:
            kwargs['state'] = DraftState.READY
        self.update(kwargs)
        # mod.inform_users(self.exclude(changed_by=None).select_related('changed_by__email'))
        post_moderation.send(
            sender=self.content_type.model_class(),
            instance=self.content_object,
            status=verdict,
        )
