from datetime import datetime
from typing import TYPE_CHECKING, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet

from apps.moderation.constants import DraftState, ModerationStatus

if TYPE_CHECKING:
    from apps.moderation.models.change import Change
    from apps.moderation.models.moderated_model import ModeratedModel


class ChangeQuerySet(QuerySet):

    model: Type['Change']

    def approve(self, cls: Type['ModeratedModel'], by, reason=None):
        self._send_signals_and_moderate(
            cls,
            ModerationStatus.APPROVED,
            by,
            reason,
        )

    def reject(self, cls: Type['ModeratedModel'], by, reason=None):
        self._send_signals_and_moderate(cls, ModerationStatus.REJECTED, by, reason)

    def _moderate(self, cls: Type['ModeratedModel'], new_status, moderator, reason):
        visibility_column = 'verified'
        ct = ContentType.objects.get_for_model(cls)
        update_kwargs = {
            'moderation_status': new_status,
            'date': datetime.now(),
            'moderator': moderator,
            'reason': reason,
        }
        if new_status == ModerationStatus.APPROVED:
            update_kwargs['state'] = DraftState.READY
        self.update(update_kwargs)
        if visibility_column:
            if new_status == ModerationStatus.APPROVED:
                new_visible = True
            else:
                new_visible = False
            cls.objects.filter(
                id__in=self.filter(content_type=ct).values_list('object_id', flat=True)
            ).update(**{visibility_column: new_visible})
        # mod.inform_users(self.exclude(changed_by=None).select_related('changed_by__email'))
