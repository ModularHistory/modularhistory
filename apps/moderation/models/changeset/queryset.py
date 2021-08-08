from datetime import datetime
from typing import TYPE_CHECKING, Optional, Type

from django.db.models.query import QuerySet

from apps.moderation.constants import DraftState, ModerationStatus

if TYPE_CHECKING:
    from apps.moderation.models.changeset import ChangeSet
    from apps.users.models import User


class ChangeSetQuerySet(QuerySet):

    model: Type['ChangeSet']

    def approve(self, moderator: Optional['User'], reason: Optional[str] = None):
        """Approve the change sets."""
        self._moderate(
            verdict=ModerationStatus.APPROVED,
            moderator=moderator,
            reason=reason,
        )

    def reject(self, moderator: Optional['User'], reason=None):
        """Reject the change sets."""
        self._moderate(ModerationStatus.REJECTED, moderator, reason)

    def _moderate(
        self,
        verdict: int,
        moderator: Optional['User'],
        reason: Optional[str] = None,
    ):
        """Update the moderation status of the change sets."""
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
