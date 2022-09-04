from datetime import datetime
from typing import TYPE_CHECKING, Optional

from django.db import transaction
from django.db.models.query import QuerySet

from apps.moderation.constants import ModerationStatus

if TYPE_CHECKING:
    from apps.moderation.models.change import Change
    from apps.users.models import User


class ChangeQuerySet(QuerySet):
    """Lazy database lookup for a set of `Change` instances."""

    model: type['Change']

    def apply(self):
        """Apply the changes to their referenced model instances."""
        change: 'Change'
        with transaction.atomic():
            for change in self.all():
                change.apply()

    def approve(self, moderator: Optional['User'], reason: Optional[str] = None):
        """Approve the changes."""
        change: 'Change'
        for change in self.all():
            change.approve(moderator=moderator, reason=reason)

    def reject(self, moderator: Optional['User'], reason: Optional[str] = None):
        """Reject the changes."""
        self.update(
            {
                'moderation_status': ModerationStatus.REJECTED,
                'date': datetime.now(),
                'moderator': moderator,
                'reason': reason,
            }
        )
