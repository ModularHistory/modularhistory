from typing import TYPE_CHECKING, Optional

from django.db.models.query import QuerySet

if TYPE_CHECKING:
    from apps.moderation.models.changeset import ChangeSet
    from apps.users.models import User


class ChangeSetQuerySet(QuerySet):

    model: type['ChangeSet']

    def approve(self, moderator: Optional['User'], reason: Optional[str] = None):
        """Approve the change sets."""
        change_set: 'ChangeSet'
        for change_set in self.all():
            change_set.changes.all().approve(moderator=moderator, reason=reason)

    def reject(self, moderator: Optional['User'], reason=None):
        """Reject the change sets."""
        change_set: 'ChangeSet'
        for change_set in self.all():
            change_set.changes.all().reject(moderator=moderator, reason=reason)
