from typing import TYPE_CHECKING, Type

from django.db.models.manager import Manager

from apps.moderation.models.changeset.queryset import ChangeSetQuerySet

if TYPE_CHECKING:
    from apps.moderation.models.changeset import ChangeSet


class ChangeSetManager(Manager):

    model: Type['ChangeSet']

    def get_queryset(self):
        return ChangeSetQuerySet(self.model, using=self._db)
