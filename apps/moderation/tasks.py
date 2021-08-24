from typing import TYPE_CHECKING, Optional

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.moderation import Approval
from core.celery import app

if TYPE_CHECKING:
    from apps.moderation.models.change import Change
    from apps.moderation.models.changeset import ChangeSet
    from apps.moderation.models.moderated_model import ModeratedModel


@app.task
def handle_approval(approval_id: int):
    """Post-process an approval."""
    approval: Approval = Approval.objects.get(pk=approval_id)
    change: 'Change' = approval.change
    if change.n_remaining_approvals_required == 0:
        # The change has enough approvals; update its status to "approved"
        # and set the `verified` field on the changed object.
        change.moderation_status = ModerationStatus.APPROVED
        changed_object: 'ModeratedModel' = change.changed_object
        changed_object.verified = True
        change.save()

        # Check if the status of the change's associated change set can also be updated.
        change_set: Optional['ChangeSet'] = change.set
        if change_set:
            if change_set.changes.exclude(
                moderation_status=ModerationStatus.APPROVED
            ).exists():
                pass
            else:
                # All changes in the set have been approved; update the set accordingly.
                change_set.moderation_status = ModerationStatus.APPROVED
                change_set.save()
                # Apply the change set.
                change_set.apply()
        else:
            # Apply the change.
            change.apply()

    # Notify users of the approval.
    approval.notify_users()
