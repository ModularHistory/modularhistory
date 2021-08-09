from typing import TYPE_CHECKING

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.moderation import Approval
from core.celery import app

if TYPE_CHECKING:
    from apps.moderation.models.change import Change


@app.task
def handle_approval(approval_id: int):
    """Post-process an approval."""
    approval: Approval = Approval.objects.get(pk=approval_id)
    change: 'Change' = approval.change
    print(f'Debugging: {approval=} {change=}')
