import logging
from typing import TYPE_CHECKING, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.moderated_model.manager import (
    ModeratedModelManager,
    SearchableModeratedModelManager,
)
from apps.moderation.moderator import GenericModerator
from apps.search.models.searchable_model import SearchableModel

if TYPE_CHECKING:
    from apps.moderation.models.change import Change


class ModeratedModel(models.Model):
    """Base class for models of which instances must be moderated."""

    modifications = GenericRelation(to='moderation.Change')

    # This field is used to decide whether model instances should be visible.
    verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
    )

    objects = ModeratedModelManager()

    class Meta:
        abstract = True

    @property
    def change_in_progress(self) -> Optional['Change']:
        return (
            self.modifications.filter(moderation_status=ModerationStatus.PENDING).first()
            if self.has_change_in_progress
            else None
        )

    @property
    def has_change_in_progress(self) -> bool:
        try:
            return self.modifications.filter(
                moderation_status=ModerationStatus.PENDING
            ).exists()
        except Exception as err:
            logging.error(err)
            return False

    class Moderator(GenericModerator):
        """Base moderator class for moderated models."""

        visibility_column = 'verified'

        # Allow multiple moderations per registered model instance.
        keep_history = True

        # Exclude fields from the object change list.
        fields_exclude = ['cache']

        auto_approve_for_staff = auto_approve_for_superusers = False

        def is_auto_approve(self, obj, user):
            """Determine whether to automatically approve a change."""
            return super().is_auto_approve(obj, user)

        def is_auto_reject(self, obj, user):
            """Determine whether to automatically reject a change."""
            return super().is_auto_reject(obj, user)


class SearchableModeratedModel(SearchableModel, ModeratedModel):
    """Base class for moderated models of which users can search for instances."""

    objects = SearchableModeratedModelManager()

    class Meta:
        abstract = True
