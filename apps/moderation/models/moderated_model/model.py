import logging
from typing import Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.change import Change
from apps.moderation.models.moderated_model.manager import (
    ModeratedModelManager,
    SearchableModeratedModelManager,
)
from apps.search.models.searchable_model import SearchableModel


class ModeratedModel(models.Model):
    """Base class for models of which instances must be moderated."""

    changes = GenericRelation(to='moderation.Change')

    # This field is used to determine whether model instances should be visible to users.
    verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
    )

    objects = ModeratedModelManager()

    class Meta:
        abstract = True

    class Moderation:
        excluded_fields = ['cache']

    @property
    def change_in_progress(self) -> Optional['Change']:
        return (
            self.changes.filter(moderation_status=ModerationStatus.PENDING).first()
            if self.has_change_in_progress
            else None
        )

    @property
    def has_change_in_progress(self) -> bool:
        try:
            return self.changes.filter(moderation_status=ModerationStatus.PENDING).exists()
        except Exception as err:
            logging.error(err)
            return False


class SearchableModeratedModel(SearchableModel, ModeratedModel):
    """Base class for moderated models of which users can search for instances."""

    objects = SearchableModeratedModelManager()

    class Meta:
        abstract = True
