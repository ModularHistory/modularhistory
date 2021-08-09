from typing import TYPE_CHECKING

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.moderation import Moderation
from core.celery import app

if TYPE_CHECKING:
    from apps.moderation.models.change import Change


def _handle_approval(approval: Moderation, change: 'Change'):
    pass


def _handle_rejection(rejection: Moderation, change: 'Change'):
    pass


@app.task
def handle_moderation(moderation_id: int):
    """Post-process a moderation."""
    moderation: Moderation = Moderation.objects.get(pk=moderation_id)
    change: 'Change' = moderation.change
    if moderation.verdict == ModerationStatus.APPROVED:
        _handle_approval(moderation, change)
    elif moderation.verdict == ModerationStatus.REJECTED:
        _handle_rejection(moderation, change)
    print(f'Debugging: {moderation=}')
