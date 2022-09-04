from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db.models.manager import Manager

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.change.queryset import ChangeQuerySet

if TYPE_CHECKING:
    from apps.moderation.models.change import Change
    from apps.moderation.models.moderated_model import ModeratedModel


class ChangeManager(Manager):

    model: type['Change']

    def get_queryset(self):
        return ChangeQuerySet(self.model, using=self._db)

    def get_for_instance(self, instance: 'ModeratedModel'):
        """Return the in-progress change for a moderated model instance."""
        return self.filter(
            object_id=instance.pk,
            content_type=ContentType.objects.get_for_model(instance.__class__),
            moderation_status__gt=ModerationStatus.REJECTED,
            merged_date__isnull=True,
        )[0]
